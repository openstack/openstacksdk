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
#


from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from openstack.image.iterable_chunked_file import IterableChunkedFile

HASH_METHODS = {
    'SHA-224': hashes.SHA224(),
    'SHA-256': hashes.SHA256(),
    'SHA-384': hashes.SHA384(),
    'SHA-512': hashes.SHA512(),
}


class ImageSigner(object):
    """Image file signature generator.

    Generates signatures for files using a specified private key file.
    """

    def __init__(self, hash_method='SHA-256', padding_method='RSA-PSS'):
        padding_types = {
            'RSA-PSS': padding.PSS(
                mgf=padding.MGF1(HASH_METHODS[hash_method]),
                salt_length=padding.PSS.MAX_LENGTH
            )
        }
        # informational attributes
        self.hash_method = hash_method
        self.padding_method = padding_method
        # runtime objects
        self.private_key = None
        self.hash = HASH_METHODS[hash_method]
        self.hasher = hashes.Hash(self.hash, default_backend())
        self.padding = padding_types[padding_method]

    def load_private_key(self, file_path, password=None):
        with open(file_path, 'rb') as key_file:
            self.private_key = serialization.load_pem_private_key(
                key_file.read(), password=password, backend=default_backend()
            )

    def generate_signature(self, file_obj):
        file_obj.seek(0)
        chunked_file = IterableChunkedFile(file_obj)
        for chunk in chunked_file:
            self.hasher.update(chunk)
        file_obj.seek(0)
        digest = self.hasher.finalize()
        signature = self.private_key.sign(
            digest, self.padding, utils.Prehashed(self.hash)
        )
        return signature
