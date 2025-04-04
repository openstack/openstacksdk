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

"""Helpers for building configdrive compatible with the Bare Metal service."""

import base64
import contextlib
import gzip
import json
import os
import shutil
import subprocess
import tempfile
import typing as ty


@contextlib.contextmanager
def populate_directory(
    metadata,
    user_data=None,
    versions=None,
    network_data=None,
    vendor_data=None,
):
    """Populate a directory with configdrive files.

    :param dict metadata: Metadata.
    :param bytes user_data: Vendor-specific user data.
    :param versions: List of metadata versions to support.
    :param dict network_data: Networking configuration.
    :param dict vendor_data: Extra supplied vendor data.
    :return: a context manager yielding a directory with files
    """
    d = tempfile.mkdtemp()
    versions = versions or ('2012-08-10', 'latest')
    try:
        for version in versions:
            subdir = os.path.join(d, 'openstack', version)
            if not os.path.exists(subdir):
                os.makedirs(subdir)

            with open(os.path.join(subdir, 'meta_data.json'), 'w') as fp:
                json.dump(metadata, fp)

            if network_data:
                with open(
                    os.path.join(subdir, 'network_data.json'), 'w'
                ) as fp:
                    json.dump(network_data, fp)

            if vendor_data:
                with open(
                    os.path.join(subdir, 'vendor_data2.json'), 'w'
                ) as fp:
                    json.dump(vendor_data, fp)

            if user_data:
                # Strictly speaking, user data is binary, but in many cases
                # it's actually a text (cloud-init, ignition, etc).
                flag = 't' if isinstance(user_data, str) else 'b'
                with open(os.path.join(subdir, 'user_data'), f'w{flag}') as fp:
                    fp.write(user_data)

        yield d
    finally:
        shutil.rmtree(d)


def build(
    metadata,
    user_data=None,
    versions=None,
    network_data=None,
    vendor_data=None,
):
    """Make a configdrive compatible with the Bare Metal service.

    Requires the genisoimage utility to be available.

    :param dict metadata: Metadata.
    :param user_data: Vendor-specific user data.
    :param versions: List of metadata versions to support.
    :param dict network_data: Networking configuration.
    :param dict vendor_data: Extra supplied vendor data.
    :return: configdrive contents as a base64-encoded string.
    """
    with populate_directory(
        metadata, user_data, versions, network_data, vendor_data
    ) as path:
        return pack(path)


def pack(path: str) -> str:
    """Pack a directory with files into a Bare Metal service configdrive.

    Creates an ISO image with the files and label "config-2".

    :param str path: Path to directory with files
    :return: configdrive contents as a base64-encoded string.
    """
    with tempfile.NamedTemporaryFile() as tmpfile:
        # NOTE(toabctl): Luckily, genisoimage, mkisofs and xorrisofs understand
        # the same parameters which are currently used.
        error: ty.Optional[Exception]
        for c in ['genisoimage', 'mkisofs', 'xorrisofs']:
            try:
                p = subprocess.Popen(  # noqa: S603
                    [
                        c,
                        '-o',
                        tmpfile.name,
                        '-ldots',
                        '-allow-lowercase',
                        '-allow-multidot',
                        '-l',
                        '-publisher',
                        'metalsmith',
                        '-quiet',
                        '-J',
                        '-r',
                        '-V',
                        'config-2',
                        path,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except OSError as e:
                error = e
            else:
                error = None
                break

        if error:
            raise RuntimeError(
                'Error generating the configdrive. Make sure the '
                '"genisoimage", "mkisofs" or "xorrisofs" tool is installed. '
                f'Error: {error}'
            )

        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise RuntimeError(
                'Error generating the configdrive.'
                f'Stdout: "{stdout.decode()}". Stderr: "{stderr.decode()}"'
            )

        tmpfile.seek(0)

        with tempfile.NamedTemporaryFile() as tmpzipfile:
            with gzip.GzipFile(fileobj=tmpzipfile, mode='wb') as gz_file:
                shutil.copyfileobj(tmpfile, gz_file)

            tmpzipfile.seek(0)
            # NOTE(dtantsur): Ironic expects configdrive to be a string, but
            # base64 returns bytes on Python 3.
            cd = base64.b64encode(tmpzipfile.read()).decode()

    return cd
