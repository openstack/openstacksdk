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

from openstack.tests.unit import base

from openstack.orchestration.v1 import software_config


FAKE_ID = 'ce8ae86c-9810-4cb1-8888-7fb53bc523bf'
FAKE_NAME = 'test_software_config'
FAKE = {
    'id': FAKE_ID,
    'name': FAKE_NAME,
    'config': 'fake config',
    'creation_time': '2015-03-09T12:15:57',
    'group': 'fake group',
    'inputs': [{'foo': 'bar'}],
    'outputs': [{'baz': 'zoo'}],
    'options': {'key': 'value'},
}


class TestSoftwareConfig(base.TestCase):

    def test_basic(self):
        sot = software_config.SoftwareConfig()
        self.assertEqual('software_config', sot.resource_key)
        self.assertEqual('software_configs', sot.resources_key)
        self.assertEqual('/software_configs', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = software_config.SoftwareConfig(**FAKE)
        self.assertEqual(FAKE_ID, sot.id)
        self.assertEqual(FAKE_NAME, sot.name)
        self.assertEqual(FAKE['config'], sot.config)
        self.assertEqual(FAKE['creation_time'], sot.created_at)
        self.assertEqual(FAKE['group'], sot.group)
        self.assertEqual(FAKE['inputs'], sot.inputs)
        self.assertEqual(FAKE['outputs'], sot.outputs)
        self.assertEqual(FAKE['options'], sot.options)
