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

from openstack.accelerator.v2 import attribute as _attribute
from openstack.tests.functional import base


class TestAttribute(base.BaseFunctionalTest):
    """Test attribute CRUD.

    Attributes are key-value pairs attached to a deployable. The fake
    driver creates a deployable on startup which we use as the parent.
    """

    def setUp(self):
        super().setUp()
        self.require_service('accelerator')
        deployables = list(self.operator_cloud.accelerator.deployables())
        self.assertGreater(
            len(deployables),
            0,
            'no deployables found: is the fake driver enabled?',
        )
        self.deployable_id = deployables[0].id

    def _delete_attribute(self, attr):
        self.operator_cloud.accelerator.delete_attribute(attr)
        attrs = list(self.operator_cloud.accelerator.attributes())
        uuids = [a.uuid for a in attrs]
        self.assertNotIn(attr.uuid, uuids)

    def test_attribute(self):
        # TODO(melwitt): unskip once LP#2158996 is fixed
        self.skipTest(
            'Cyborg attribute API requires internal DB integer for '
            'deployable_id (LP#2158996)'
        )
        attr = self.operator_cloud.accelerator.create_attribute(
            deployable_id=self.deployable_id,
            key='test_key',
            value='test_value',
        )
        self.assertIsInstance(attr, _attribute.Attribute)
        self.addCleanup(self._delete_attribute, attr)

        # Get
        got = self.operator_cloud.accelerator.get_attribute(attr.uuid)
        self.assertIsInstance(got, _attribute.Attribute)
        self.assertEqual('test_key', got.key)
        self.assertEqual('test_value', got.value)

        # List
        attrs = list(self.operator_cloud.accelerator.attributes())
        uuids = [a.uuid for a in attrs]
        self.assertIn(attr.uuid, uuids)
