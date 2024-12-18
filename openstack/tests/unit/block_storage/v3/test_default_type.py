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

from unittest import mock

from keystoneauth1 import adapter

from openstack.block_storage.v3 import default_type
from openstack.tests.unit import base


PROJECT_ID = 'd5e678b5-f88b-411c-876b-f6ec2ba999bf'
VOLUME_TYPE_ID = 'adef1cf8-736e-4b62-a2db-f8b6b6c1d953'

DEFAULT_TYPE = {
    'project_id': PROJECT_ID,
    'volume_type_id': VOLUME_TYPE_ID,
}


class TestDefaultType(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.status_code = 200
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.default_microversion = '3.67'
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess._get_connection = mock.Mock(return_value=self.cloud)

    def test_basic(self):
        sot = default_type.DefaultType(**DEFAULT_TYPE)
        self.assertEqual("default_type", sot.resource_key)
        self.assertEqual("default_types", sot.resources_key)
        self.assertEqual("/default-types", sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_create(self):
        sot = default_type.DefaultType(**DEFAULT_TYPE)
        self.assertEqual(DEFAULT_TYPE["project_id"], sot.project_id)
        self.assertEqual(DEFAULT_TYPE["volume_type_id"], sot.volume_type_id)
