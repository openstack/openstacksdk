# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import collections.abc
import hashlib
import io
import typing as ty

from openstack import exceptions
from openstack import utils


def _verify_checksum(
    hasher: ty.Any,
    expected_hash: str | None,
    hash_algo: str | None = None,
) -> None:
    """Verify checksum using the provided hasher.

    :param hasher: A hashlib hash object
    :param expected_hash: The expected hexdigest value
    :param hash_algo: Optional name of the hash algorithm for error messages
    :raises: InvalidResponse if the hash doesn't match
    """
    if expected_hash:
        digest = hasher.hexdigest()
        if digest != expected_hash:
            algo_msg = f" ({hash_algo})" if hash_algo else ""
            raise exceptions.InvalidResponse(
                f"checksum mismatch{algo_msg}: {expected_hash} != {digest}"
            )


def _integrity_iter(
    iterable: collections.abc.Iterable[bytes],
    hasher: ty.Any,
    expected_hash: str | None,
    hash_algo: str | None,
) -> collections.abc.Iterator[bytes]:
    """Check image data integrity

    :param iterable: Iterable containing the image data chunks
    :param hasher: A hashlib hash object
    :param expected_hash: The expected hexdigest value
    :param hash_algo: The hash algorithm
    :yields: Chunks of data while computing hash
    :raises: InvalidResponse if the hash doesn't match
    """
    for chunk in iterable:
        hasher.update(chunk)
        yield chunk
    _verify_checksum(hasher, expected_hash, hash_algo)


def _write_chunks(
    fd: io.IOBase, chunks: collections.abc.Iterable[bytes]
) -> None:
    """Write chunks to file descriptor."""
    for chunk in chunks:
        fd.write(chunk)


class DownloadMixin:
    id: str
    base_path: str

    def fetch(
        self,
        session,
        requires_id=True,
        base_path=None,
        error_message=None,
        skip_cache=False,
        *,
        resource_response_key=None,
        microversion=None,
        **params,
    ): ...

    def download(
        self, session, stream=False, output=None, chunk_size=1024 * 1024
    ):
        """Download the data contained in an image.

        Checksum validation uses the hash algorithm metadata fields
        (hash_value + hash_algo) if available, otherwise falls back to MD5 via
        'checksum' or 'Content-MD5'. No validation is performed if neither is
        available.
        """

        # Fetch image metadata first to get hash info before downloading.
        # This prevents race conditions and the need for a second conditional
        # metadata retrieval if Content-MD5 is missing (story/1619675).
        details = self.fetch(session)
        meta_checksum = getattr(details, 'checksum', None)
        meta_hash_value = getattr(details, 'hash_value', None)
        meta_hash_algo = getattr(details, 'hash_algo', None)

        url = utils.urljoin(self.base_path, self.id, 'file')
        resp = session.get(url, stream=stream)

        hasher = None
        expected_hash = None
        hash_algo = None
        header_checksum = resp.headers.get("Content-MD5")

        if meta_hash_value and meta_hash_algo:
            try:
                hasher = hashlib.new(str(meta_hash_algo))
                expected_hash = meta_hash_value
                hash_algo = meta_hash_algo
            except ValueError as ve:
                if not str(ve).startswith('unsupported hash type'):
                    raise exceptions.SDKException(
                        f"Unsupported hash algorithm '{meta_hash_algo}': {ve}"
                    )

        # Fall back to MD5 from metadata or header
        if not hasher:
            md5_source = meta_checksum or header_checksum
            if md5_source:
                hasher = hashlib.md5(usedforsecurity=False)
                expected_hash = md5_source
                hash_algo = 'md5'

        if hasher is None:
            session.log.warning(
                "Unable to verify the integrity of image %s "
                "- no hash available",
                self.id,
            )

        if output:
            try:
                chunks = resp.iter_content(chunk_size=chunk_size)
                if hasher is not None:
                    chunks = _integrity_iter(
                        chunks, hasher, expected_hash, hash_algo
                    )

                if isinstance(output, io.IOBase):
                    _write_chunks(output, chunks)
                else:
                    with open(output, 'wb') as fd:
                        _write_chunks(fd, chunks)

                return resp
            except Exception as e:
                raise exceptions.SDKException(f"Unable to download image: {e}")

        if stream:
            # Set content-md5 header for backward compatibility with callers
            # who expect hash info in the response when streaming
            if hash_algo == 'md5' and expected_hash:
                resp.headers['content-md5'] = expected_hash
            return resp

        if hasher is not None:
            # Loads entire image into memory!
            hasher.update(resp.content)
            _verify_checksum(hasher, expected_hash, hash_algo)

        return resp
