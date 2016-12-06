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

import testtools

from openstack.cluster.v1 import profile


FAKE_ID = '9b127538-a675-4271-ab9b-f24f54cfe173'
FAKE_NAME = 'test_profile'

FAKE = {
    'metadata': {},
    'name': FAKE_NAME,
    'id': FAKE_ID,
    'spec': {
        'type': 'os.nova.server',
        'version': 1.0,
        'properties': {
            'flavor': 1,
            'image': 'cirros-0.3.2-x86_64-uec',
            'key_name': 'oskey',
            'name': 'cirros_server'
        }
    },
    'project': '42d9e9663331431f97b75e25136307ff',
    'user': '3747afc360b64702a53bdd64dc1b8976',
    'type': 'os.nova.server',
    'created_at': '2015-10-10T12:46:36.000000',
    'updated_at': '2016-10-10T12:46:36.000000',
}


class TestProfile(testtools.TestCase):

    def setUp(self):
        super(TestProfile, self).setUp()

    def test_basic(self):
        sot = profile.Profile()
        self.assertEqual('profile', sot.resource_key)
        self.assertEqual('profiles', sot.resources_key)
        self.assertEqual('/profiles', sot.base_path)
        self.assertEqual('clustering', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_update)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.patch_update)

    def test_instantiate(self):
        sot = profile.Profile(**FAKE)
        self.assertEqual(FAKE['id'], sot.id)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['metadata'], sot.metadata)
        self.assertEqual(FAKE['spec'], sot.spec)
        self.assertEqual(FAKE['project'], sot.project_id)
        self.assertEqual(FAKE['user'], sot.user_id)
        self.assertEqual(FAKE['type'], sot.type)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)


class TestProfileValidate(testtools.TestCase):

    def setUp(self):
        super(TestProfileValidate, self).setUp()

    def test_basic(self):
        sot = profile.ProfileValidate()
        self.assertEqual('profile', sot.resource_key)
        self.assertEqual('profiles', sot.resources_key)
        self.assertEqual('/profiles/validate', sot.base_path)
        self.assertEqual('clustering', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_get)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)
        self.assertFalse(sot.patch_update)
