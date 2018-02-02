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

from openstack.compute.v2 import hypervisor

EXAMPLE = {
    "status": "enabled",
    "service": {
        "host": "fake-mini",
        "disabled_reason": None,
        "id": 6
    },
    "vcpus_used": 0,
    "hypervisor_type": "QEMU",
    "local_gb_used": 0,
    "vcpus": 8,
    "hypervisor_hostname": "fake-mini",
    "memory_mb_used": 512,
    "memory_mb": 7980,
    "current_workload": 0,
    "state": "up",
    "host_ip": "23.253.248.171",
    "cpu_info": "some cpu info",
    "running_vms": 0,
    "free_disk_gb": 157,
    "hypervisor_version": 2000000,
    "disk_available_least": 140,
    "local_gb": 157,
    "free_ram_mb": 7468,
    "id": 1
}


class TestHypervisor(base.TestCase):

    def test_basic(self):
        sot = hypervisor.Hypervisor()
        self.assertEqual('hypervisor', sot.resource_key)
        self.assertEqual('hypervisors', sot.resources_key)
        self.assertEqual('/os-hypervisors', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertTrue(sot.allow_get)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = hypervisor.Hypervisor(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['hypervisor_hostname'], sot.name)
        self.assertEqual(EXAMPLE['state'], sot.state)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['service'], sot.service_details)
        self.assertEqual(EXAMPLE['vcpus_used'], sot.vcpus_used)
        self.assertEqual(EXAMPLE['hypervisor_type'], sot.hypervisor_type)
        self.assertEqual(EXAMPLE['local_gb_used'], sot.local_disk_used)
        self.assertEqual(EXAMPLE['vcpus'], sot.vcpus)
        self.assertEqual(EXAMPLE['vcpus_used'], sot.vcpus_used)
        self.assertEqual(EXAMPLE['memory_mb_used'], sot.memory_used)
        self.assertEqual(EXAMPLE['memory_mb'], sot.memory_size)
        self.assertEqual(EXAMPLE['current_workload'], sot.current_workload)
        self.assertEqual(EXAMPLE['host_ip'], sot.host_ip)
        self.assertEqual(EXAMPLE['cpu_info'], sot.cpu_info)
        self.assertEqual(EXAMPLE['running_vms'], sot.running_vms)
        self.assertEqual(EXAMPLE['free_disk_gb'], sot.local_disk_free)
        self.assertEqual(EXAMPLE['hypervisor_version'], sot.hypervisor_version)
        self.assertEqual(EXAMPLE['disk_available_least'], sot.disk_available)
        self.assertEqual(EXAMPLE['local_gb'], sot.local_disk_size)
        self.assertEqual(EXAMPLE['free_ram_mb'], sot.memory_free)
