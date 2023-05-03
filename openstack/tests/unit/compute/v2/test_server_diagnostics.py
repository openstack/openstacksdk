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

from openstack.compute.v2 import server_diagnostics
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    "config_drive": True,
    "cpu_details": [{"id": 0, "time": 17300000000, "utilisation": 15}],
    "disk_details": [
        {
            "errors_count": 1,
            "read_bytes": 262144,
            "read_requests": 112,
            "write_bytes": 5778432,
            "write_requests": 488,
        }
    ],
    "driver": "libvirt",
    "hypervisor": "kvm",
    "hypervisor_os": "ubuntu",
    "memory_details": {"maximum": 524288, "used": 0},
    "nic_details": [
        {
            "mac_address": "01:23:45:67:89:ab",
            "rx_drop": 200,
            "rx_errors": 100,
            "rx_octets": 2070139,
            "rx_packets": 26701,
            "rx_rate": 300,
            "tx_drop": 500,
            "tx_errors": 400,
            "tx_octets": 140208,
            "tx_packets": 662,
            "tx_rate": 600,
        }
    ],
    "num_cpus": 1,
    "num_disks": 1,
    "num_nics": 1,
    "state": "running",
    "uptime": 46664,
}


class TestServerInterface(base.TestCase):
    def test_basic(self):
        sot = server_diagnostics.ServerDiagnostics()
        self.assertEqual('diagnostics', sot.resource_key)
        self.assertEqual('/servers/%(server_id)s/diagnostics', sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.requires_id)

    def test_make_it(self):
        sot = server_diagnostics.ServerDiagnostics(**EXAMPLE)
        self.assertEqual(EXAMPLE['config_drive'], sot.has_config_drive)
        self.assertEqual(EXAMPLE['cpu_details'], sot.cpu_details)
        self.assertEqual(EXAMPLE['disk_details'], sot.disk_details)
        self.assertEqual(EXAMPLE['driver'], sot.driver)
        self.assertEqual(EXAMPLE['hypervisor'], sot.hypervisor)
        self.assertEqual(EXAMPLE['hypervisor_os'], sot.hypervisor_os)
        self.assertEqual(EXAMPLE['memory_details'], sot.memory_details)
        self.assertEqual(EXAMPLE['nic_details'], sot.nic_details)
        self.assertEqual(EXAMPLE['num_cpus'], sot.num_cpus)
        self.assertEqual(EXAMPLE['num_disks'], sot.num_disks)
        self.assertEqual(EXAMPLE['num_nics'], sot.num_nics)
        self.assertEqual(EXAMPLE['state'], sot.state)
        self.assertEqual(EXAMPLE['uptime'], sot.uptime)
