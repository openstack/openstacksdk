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

import testtools

from openstack.baremetal import configdrive


class TestPopulateDirectory(testtools.TestCase):
    def _check(self, metadata, user_data=None):
        with configdrive.populate_directory(metadata, user_data) as d:
            for version in ('2012-08-10', 'latest'):
                with open(os.path.join(d, 'openstack', version,
                                       'meta_data.json')) as fp:
                    actual_metadata = json.load(fp)

                self.assertEqual(metadata, actual_metadata)
                user_data_file = os.path.join(d, 'openstack', version,
                                              'user_data')
                if user_data is None:
                    self.assertFalse(os.path.exists(user_data_file))
                else:
                    with open(user_data_file, 'rb') as fp:
                        self.assertEqual(user_data, fp.read())

        # Clean up in __exit__
        self.assertFalse(os.path.exists(d))

    def test_without_user_data(self):
        self._check({'foo': 42})

    def test_with_user_data(self):
        self._check({'foo': 42}, b'I am user data')
