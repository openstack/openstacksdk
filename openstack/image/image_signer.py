#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import warnings
from typing import Any, Final, IO, cast

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import mldsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

from openstack import exceptions
from openstack.image.iterable_chunked_file import IterableChunkedFile
from openstack import warnings as os_warnings

HASH_METHODS = {
    'SHA-224': hashes.SHA224(),
    'SHA-256': hashes.SHA256(),
    'SHA-384': hashes.SHA384(),
    'SHA-512': hashes.SHA512(),
}

RSA_PSS = 'RSA-PSS'
ML_DSA_44 = 'ML-DSA-44'
ML_DSA_65 = 'ML-DSA-65'
ML_DSA_87 = 'ML-DSA-87'

SIGNATURE_ALGORITHMS: Final = {
    RSA_PSS: rsa.RSAPrivateKey,
    ML_DSA_44: mldsa.MLDSA44PrivateKey,
    ML_DSA_65: mldsa.MLDSA65PrivateKey,
    ML_DSA_87: mldsa.MLDSA87PrivateKey,
}


class ImageSigner:
    """Image file signature generator.

    Generates signatures for files using a specified private key file.

    ``signature_algorithm`` selects the signing algorithm and must be passed
    by keyword. RSA-PSS remains the default. ``padding_method`` is deprecated
    and will be removed in version 5.0.

    ML-DSA ignores ``hash_method`` because FIPS 204 uses its own external-mu
    representative. The value is still accepted because image signature
    metadata requires a hash method.
    """

    def __init__(
        self,
        hash_method: str = 'SHA-256',
        padding_method: str | None = None,
        *,
        signature_algorithm: str | None = None,
    ) -> None:
        if padding_method is not None:
            warnings.warn(
                'padding_method is deprecated and will be removed in SDK 5.0; '
                'use signature_algorithm',
                os_warnings.RemovedInSDK50Warning,
                stacklevel=2,
            )

        if signature_algorithm is None:
            signature_algorithm = padding_method or RSA_PSS
        elif (
            padding_method is not None
            and signature_algorithm != padding_method
        ):
            raise exceptions.SDKException(
                'signature_algorithm and padding_method must match'
            )

        if hash_method not in HASH_METHODS:
            raise exceptions.SDKException(
                f'Unsupported hash method: {hash_method}'
            )

        if signature_algorithm not in SIGNATURE_ALGORITHMS:
            raise exceptions.SDKException(
                f'Unsupported signature algorithm: {signature_algorithm}'
            )

        self.hash_method = hash_method
        self.signature_algorithm = signature_algorithm
        self.padding_method = signature_algorithm

        self.private_key: Any = None
        self.hash = HASH_METHODS[hash_method]
        self.hasher: Any = None
        self.padding: Any = None

        if signature_algorithm == RSA_PSS:
            self.padding = padding.PSS(
                mgf=padding.MGF1(self.hash),
                salt_length=padding.PSS.MAX_LENGTH,
            )
            self.hasher = hashes.Hash(self.hash, default_backend())

    def load_private_key(
        self, file_path: str, password: bytes | None = None
    ) -> None:
        with open(file_path, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(), password=password, backend=default_backend()
            )

        expected_key_type = SIGNATURE_ALGORITHMS[self.signature_algorithm]
        if not isinstance(private_key, expected_key_type):
            raise exceptions.SDKException(
                f'Private key does not match {self.signature_algorithm}'
            )

        if self.signature_algorithm == RSA_PSS:
            self.private_key = private_key
            return

        mldsa_private_key = cast(
            'mldsa.MLDSA44PrivateKey | mldsa.MLDSA65PrivateKey '
            '| mldsa.MLDSA87PrivateKey',
            private_key,
        )
        self.private_key = mldsa_private_key
        self.hasher = mldsa.MLDSAMuHasher(mldsa_private_key.public_key())

    def _hash_file(self, file_obj: IO[bytes]) -> None:
        file_obj.seek(0)
        for chunk in IterableChunkedFile(file_obj):
            self.hasher.update(chunk)
        file_obj.seek(0)

    def generate_signature(self, file_obj: IO[bytes]) -> bytes:
        if not self.private_key:
            raise exceptions.SDKException('private_key not set')

        self._hash_file(file_obj)

        if self.signature_algorithm == RSA_PSS:
            digest = self.hasher.finalize()
            signature = self.private_key.sign(
                digest, self.padding, utils.Prehashed(self.hash)
            )
        else:
            signature = self.private_key.sign_mu(self.hasher.finalize())

        return cast(bytes, signature)
