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

import uuid

from openstack.accelerator.v2 import deployable
from openstack.tests.unit import base


EXAMPLE = {
    'uuid': uuid.uuid4(),
    'created_at': '2019-08-09T12:14:57.233772',
    'updated_at': '2019-08-09T12:15:57.233772',
    'parent_id': '1',
    'root_id': '1',
    'name': 'test_name',
    'num_accelerators': '1',
    'device_id': '1',
}


class TestDeployable(base.TestCase):
    def test_basic(self):
        sot = deployable.Deployable()
        self.assertEqual('deployable', sot.resource_key)
        self.assertEqual('deployables', sot.resources_key)
        self.assertEqual('/deployables', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = deployable.Deployable(**EXAMPLE)
        self.assertEqual(EXAMPLE['uuid'], sot.id)
        self.assertEqual(EXAMPLE['parent_id'], sot.parent_id)
        self.assertEqual(EXAMPLE['root_id'], sot.root_id)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['num_accelerators'], sot.num_accelerators)
        self.assertEqual(EXAMPLE['device_id'], sot.device_id)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
