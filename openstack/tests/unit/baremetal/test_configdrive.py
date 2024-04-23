# Copyright 2018 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
from unittest import mock

import testtools

from openstack.baremetal import configdrive


class TestPopulateDirectory(testtools.TestCase):
    def _check(
        self, metadata, user_data=None, network_data=None, vendor_data=None
    ):
        with configdrive.populate_directory(
            metadata,
            user_data=user_data,
            network_data=network_data,
            vendor_data=vendor_data,
        ) as d:
            for version in ('2012-08-10', 'latest'):
                with open(
                    os.path.join(d, 'openstack', version, 'meta_data.json')
                ) as fp:
                    actual_metadata = json.load(fp)

                self.assertEqual(metadata, actual_metadata)
                network_data_file = os.path.join(
                    d, 'openstack', version, 'network_data.json'
                )
                user_data_file = os.path.join(
                    d, 'openstack', version, 'user_data'
                )
                vendor_data_file = os.path.join(
                    d, 'openstack', version, 'vendor_data2.json'
                )

                if network_data is None:
                    self.assertFalse(os.path.exists(network_data_file))
                else:
                    with open(network_data_file) as fp:
                        self.assertEqual(network_data, json.load(fp))

                if vendor_data is None:
                    self.assertFalse(os.path.exists(vendor_data_file))
                else:
                    with open(vendor_data_file) as fp:
                        self.assertEqual(vendor_data, json.load(fp))

                if user_data is None:
                    self.assertFalse(os.path.exists(user_data_file))
                else:
                    if isinstance(user_data, str):
                        user_data = user_data.encode()
                    with open(user_data_file, 'rb') as fp:
                        self.assertEqual(user_data, fp.read())

        # Clean up in __exit__
        self.assertFalse(os.path.exists(d))

    def test_without_user_data(self):
        self._check({'foo': 42})

    def test_with_user_data(self):
        self._check({'foo': 42}, b'I am user data')

    def test_with_user_data_as_string(self):
        self._check({'foo': 42}, 'I am user data')

    def test_with_network_data(self):
        self._check({'foo': 42}, network_data={'networks': {}})

    def test_with_vendor_data(self):
        self._check({'foo': 42}, vendor_data={'foo': 'bar'})


@mock.patch('subprocess.Popen', autospec=True)
class TestPack(testtools.TestCase):
    def test_no_genisoimage(self, mock_popen):
        mock_popen.side_effect = OSError
        self.assertRaisesRegex(
            RuntimeError, "genisoimage", configdrive.pack, "/fake"
        )

    def test_genisoimage_fails(self, mock_popen):
        mock_popen.return_value.communicate.return_value = b"", b"BOOM"
        mock_popen.return_value.returncode = 1
        self.assertRaisesRegex(RuntimeError, "BOOM", configdrive.pack, "/fake")

    def test_success(self, mock_popen):
        mock_popen.return_value.communicate.return_value = b"", b""
        mock_popen.return_value.returncode = 0
        result = configdrive.pack("/fake")
        # Make sure the result is string on all python versions
        self.assertIsInstance(result, str)
