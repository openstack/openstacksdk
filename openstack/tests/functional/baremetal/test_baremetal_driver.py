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


class TestBareMetalDriver(base.BaseBaremetalTest):
    def test_fake_hardware_get(self):
        driver = self.operator_cloud.baremetal.get_driver('fake-hardware')
        self.assertEqual('fake-hardware', driver.name)
        self.assertNotEqual([], driver.hosts)

    def test_fake_hardware_list(self):
        drivers = self.operator_cloud.baremetal.drivers()
        self.assertIn('fake-hardware', [d.name for d in drivers])

    def test_driver_negative_non_existing(self):
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.baremetal.get_driver,
            'not-a-driver',
        )


class TestBareMetalDriverDetails(base.BaseBaremetalTest):
    min_microversion = '1.30'

    def test_fake_hardware_get(self):
        driver = self.operator_cloud.baremetal.get_driver('fake-hardware')
        self.assertEqual('fake-hardware', driver.name)
        for iface in ('boot', 'deploy', 'management', 'power'):
            self.assertIn(
                'fake', getattr(driver, f'enabled_{iface}_interfaces')
            )
            self.assertEqual(
                'fake', getattr(driver, f'default_{iface}_interface')
            )
        self.assertNotEqual([], driver.hosts)

    def test_fake_hardware_list_details(self):
        drivers = self.operator_cloud.baremetal.drivers(details=True)
        driver = [d for d in drivers if d.name == 'fake-hardware'][0]
        for iface in ('boot', 'deploy', 'management', 'power'):
            self.assertIn(
                'fake', getattr(driver, f'enabled_{iface}_interfaces')
            )
            self.assertEqual(
                'fake', getattr(driver, f'default_{iface}_interface')
            )
