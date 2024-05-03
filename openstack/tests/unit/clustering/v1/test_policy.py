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

from openstack.clustering.v1 import policy
from openstack.tests.unit import base


FAKE_ID = 'ac5415bd-f522-4160-8be0-f8853e4bc332'
FAKE_NAME = 'test_policy'

FAKE = {
    'id': FAKE_ID,
    'name': FAKE_NAME,
    'spec': {
        'type': 'senlin.policy.deletion',
        'version': '1.0',
        'properties': {
            'criteria': 'OLDEST_FIRST',
            'grace_period': 60,
            'reduce_desired_capacity': False,
            'destroy_after_deletion': True,
        },
    },
    'project': '42d9e9663331431f97b75e25136307ff',
    'domain': '204ccccd267b40aea871750116b5b184',
    'user': '3747afc360b64702a53bdd64dc1b8976',
    'type': 'senlin.policy.deletion-1.0',
    'created_at': '2015-10-10T12:46:36.000000',
    'updated_at': '2016-10-10T12:46:36.000000',
    'data': {},
}


class TestPolicy(base.TestCase):
    def setUp(self):
        super().setUp()

    def test_basic(self):
        sot = policy.Policy()
        self.assertEqual('policy', sot.resource_key)
        self.assertEqual('policies', sot.resources_key)
        self.assertEqual('/policies', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_instantiate(self):
        sot = policy.Policy(**FAKE)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['spec'], sot.spec)
        self.assertEqual(FAKE['project'], sot.project_id)
        self.assertEqual(FAKE['domain'], sot.domain_id)
        self.assertEqual(FAKE['user'], sot.user_id)
        self.assertEqual(FAKE['data'], sot.data)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)


class TestPolicyValidate(base.TestCase):
    def setUp(self):
        super().setUp()

    def test_basic(self):
        sot = policy.PolicyValidate()
        self.assertEqual('policy', sot.resource_key)
        self.assertEqual('policies', sot.resources_key)
        self.assertEqual('/policies/validate', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)
