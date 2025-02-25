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


from openstack import exceptions
from openstack.tests.functional.baremetal import base


class TestBareMetalChassis(base.BaseBaremetalTest):
    def test_chassis_create_get_delete(self):
        chassis = self.create_chassis()

        loaded = self.operator_cloud.baremetal.get_chassis(chassis.id)
        self.assertEqual(loaded.id, chassis.id)

        self.operator_cloud.baremetal.delete_chassis(
            chassis, ignore_missing=False
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_chassis,
            chassis.id,
        )

    def test_chassis_update(self):
        chassis = self.create_chassis()
        chassis.extra = {'answer': 42}

        chassis = self.operator_cloud.baremetal.update_chassis(chassis)
        self.assertEqual({'answer': 42}, chassis.extra)

        chassis = self.operator_cloud.baremetal.get_chassis(chassis.id)
        self.assertEqual({'answer': 42}, chassis.extra)

    def test_chassis_patch(self):
        chassis = self.create_chassis()

        chassis = self.operator_cloud.baremetal.patch_chassis(
            chassis, dict(path='/extra/answer', op='add', value=42)
        )
        self.assertEqual({'answer': 42}, chassis.extra)

        chassis = self.operator_cloud.baremetal.get_chassis(chassis.id)
        self.assertEqual({'answer': 42}, chassis.extra)

    def test_chassis_negative_non_existing(self):
        uuid = "5c9dcd04-2073-49bc-9618-99ae634d8971"
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_chassis,
            uuid,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.find_chassis,
            uuid,
            ignore_missing=False,
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.delete_chassis,
            uuid,
            ignore_missing=False,
        )
        self.assertIsNone(self.operator_cloud.baremetal.find_chassis(uuid))
        self.assertIsNone(self.operator_cloud.baremetal.delete_chassis(uuid))


class TestBareMetalChassisFields(base.BaseBaremetalTest):
    min_microversion = '1.8'

    def test_chassis_fields(self):
        self.create_chassis(description='something')
        result = self.operator_cloud.baremetal.chassis(
            fields=['uuid', 'extra']
        )
        for ch in result:
            self.assertIsNotNone(ch.id)
            self.assertIsNone(ch.description)
