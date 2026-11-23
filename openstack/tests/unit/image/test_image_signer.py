# Copyright (C) 2026 RedHat Inc.
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

import io
import os
import tempfile
from typing import BinaryIO
from typing import cast

from cryptography.exceptions import InvalidSignature
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import mldsa
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

from openstack import exceptions
from openstack.image import image_signer
from openstack.tests.unit import base
from openstack import warnings as os_warnings


STREAM_CHUNK_SIZE = 1024 * 1024
STREAM_CHUNK_COUNT = 129
MldsaPrivateKey = (
    mldsa.MLDSA44PrivateKey | mldsa.MLDSA65PrivateKey | mldsa.MLDSA87PrivateKey
)


class MultiChunkStream(io.RawIOBase):
    """Simulate a large file without allocating its full contents."""

    def __init__(self, payload, chunk_count):
        super().__init__()
        self.payload = payload
        self.chunk_count = chunk_count
        self.remaining_chunks = chunk_count
        self.total_reads = 0

    def read(self, size=-1):
        if not self.remaining_chunks:
            return b''

        self.remaining_chunks -= 1
        self.total_reads += 1
        return self.payload

    def seek(self, offset, whence=0):
        if offset != 0 or whence != 0:
            raise ValueError('Only seek to the start is supported')

        self.remaining_chunks = self.chunk_count


class TestImageSigner(base.TestCase):
    def setUp(self):
        super().setUp()
        self.data = b'openstack-image-signature-test-data\n'
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.rsa_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )
        self.rsa_key_path = self._write_private_key(self.rsa_key)

    def _write_private_key(self, private_key):
        key_path = os.path.join(self.temp_dir.name, 'private-key.pem')
        with open(key_path, 'wb') as key_file:
            key_file.write(
                private_key.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption(),
                )
            )
        return key_path

    def test_default_algorithm_is_rsa_pss(self):
        signer = image_signer.ImageSigner()

        self.assertEqual(image_signer.RSA_PSS, signer.signature_algorithm)
        self.assertEqual(image_signer.RSA_PSS, signer.padding_method)

    def test_signature_algorithm_alias(self):
        signer = image_signer.ImageSigner(
            signature_algorithm=image_signer.ML_DSA_65
        )

        self.assertEqual(image_signer.ML_DSA_65, signer.signature_algorithm)
        self.assertEqual(image_signer.ML_DSA_65, signer.padding_method)

    def test_signature_algorithm_is_keyword_only(self):
        self.assertRaises(
            TypeError,
            image_signer.ImageSigner,
            'SHA-256',
            None,
            image_signer.ML_DSA_65,
        )

    def test_padding_method_alias(self):
        with self.assertWarnsRegex(
            os_warnings.RemovedInSDK50Warning,
            'padding_method is deprecated and will be removed in SDK 5.0',
        ):
            signer = image_signer.ImageSigner(
                padding_method=image_signer.ML_DSA_65
            )

        self.assertEqual(image_signer.ML_DSA_65, signer.signature_algorithm)

    def test_positional_padding_method_alias(self):
        with self.assertWarnsRegex(
            os_warnings.RemovedInSDK50Warning,
            'padding_method is deprecated and will be removed in SDK 5.0',
        ):
            signer = image_signer.ImageSigner(
                'SHA-256', image_signer.ML_DSA_65
            )

        self.assertEqual(image_signer.ML_DSA_65, signer.signature_algorithm)

    def test_conflicting_algorithm_parameters(self):
        self.assertRaisesRegex(
            exceptions.SDKException,
            'signature_algorithm and padding_method must match',
            image_signer.ImageSigner,
            signature_algorithm=image_signer.ML_DSA_65,
            padding_method=image_signer.RSA_PSS,
        )

    def test_unsupported_algorithm(self):
        self.assertRaisesRegex(
            exceptions.SDKException,
            'Unsupported signature algorithm',
            image_signer.ImageSigner,
            signature_algorithm='ML-DSA-99',
        )

    def test_unsupported_hash_method(self):
        self.assertRaisesRegex(
            exceptions.SDKException,
            'Unsupported hash method',
            image_signer.ImageSigner,
            hash_method='SHA-3-256',
        )

    def test_private_key_algorithm_mismatch(self):
        signer = image_signer.ImageSigner(
            signature_algorithm=image_signer.ML_DSA_65
        )

        self.assertRaisesRegex(
            exceptions.SDKException,
            'Private key does not match ML-DSA-65',
            signer.load_private_key,
            self.rsa_key_path,
        )

    def test_rsa_pss_signature(self):
        signer = image_signer.ImageSigner()
        signer.load_private_key(self.rsa_key_path)

        signature = signer.generate_signature(io.BytesIO(self.data))

        digest = hashes.Hash(signer.hash, default_backend())
        digest.update(self.data)
        self.rsa_key.public_key().verify(
            signature,
            digest.finalize(),
            signer.padding,
            utils.Prehashed(signer.hash),
        )

    def test_mldsa_signatures(self):
        try:
            private_keys: dict[str, MldsaPrivateKey] = {
                image_signer.ML_DSA_44: mldsa.MLDSA44PrivateKey.generate(),
                image_signer.ML_DSA_65: mldsa.MLDSA65PrivateKey.generate(),
                image_signer.ML_DSA_87: mldsa.MLDSA87PrivateKey.generate(),
            }
        except UnsupportedAlgorithm:
            self.skipTest('cryptography backend does not support ML-DSA')

        for algorithm, private_key in private_keys.items():
            key_path = self._write_private_key(private_key)
            signer = image_signer.ImageSigner(signature_algorithm=algorithm)
            signer.load_private_key(key_path)

            signature = signer.generate_signature(io.BytesIO(self.data))

            public_key = private_key.public_key()
            hasher = mldsa.MLDSAMuHasher(public_key)
            hasher.update(self.data)
            public_key.verify_mu(signature, hasher.finalize())

            tampered_data = self.data[:-1] + bytes([self.data[-1] ^ 1])
            tampered_hasher = mldsa.MLDSAMuHasher(public_key)
            tampered_hasher.update(tampered_data)
            with self.assertRaises(InvalidSignature):
                public_key.verify_mu(signature, tampered_hasher.finalize())

    def test_mldsa_large_file_streaming(self):
        try:
            private_key = mldsa.MLDSA65PrivateKey.generate()
        except UnsupportedAlgorithm:
            self.skipTest('cryptography backend does not support ML-DSA')

        key_path = self._write_private_key(private_key)
        raw_stream = MultiChunkStream(
            b'x' * STREAM_CHUNK_SIZE, STREAM_CHUNK_COUNT
        )
        stream = cast(BinaryIO, raw_stream)
        signer = image_signer.ImageSigner(
            signature_algorithm=image_signer.ML_DSA_65
        )
        signer.load_private_key(key_path)

        signature = signer.generate_signature(stream)

        self.assertEqual(STREAM_CHUNK_COUNT, raw_stream.total_reads)
        hasher = mldsa.MLDSAMuHasher(private_key.public_key())
        for _ in range(STREAM_CHUNK_COUNT):
            hasher.update(raw_stream.payload)
        private_key.public_key().verify_mu(signature, hasher.finalize())
