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

from openstack.block_storage.v3 import capabilities
from openstack.tests.unit import base

CAPABILITIES = {
    "namespace": "OS::Storage::Capabilities::fake",
    "vendor_name": "OpenStack",
    "volume_backend_name": "lvmdriver-1",
    "pool_name": "pool",
    "driver_version": "2.0.0",
    "storage_protocol": "iSCSI",
    "display_name": "Capabilities of Cinder LVM driver",
    "description": "These are volume type options",
    "visibility": "public",
    "replication_targets": [],
    "properties": {
        "compression": {
            "title": "Compression",
            "description": "Enables compression.",
            "type": "boolean",
        },
        "qos": {
            "title": "QoS",
            "description": "Enables QoS.",
            "type": "boolean",
        },
        "replication": {
            "title": "Replication",
            "description": "Enables replication.",
            "type": "boolean",
        },
        "thin_provisioning": {
            "title": "Thin Provisioning",
            "description": "Sets thin provisioning.",
            "type": "boolean",
        },
    },
}


class TestCapabilites(base.TestCase):
    def test_basic(self):
        capabilities_resource = capabilities.Capabilities()
        self.assertEqual(None, capabilities_resource.resource_key)
        self.assertEqual(None, capabilities_resource.resources_key)
        self.assertEqual("/capabilities", capabilities_resource.base_path)
        self.assertTrue(capabilities_resource.allow_fetch)
        self.assertFalse(capabilities_resource.allow_create)
        self.assertFalse(capabilities_resource.allow_commit)
        self.assertFalse(capabilities_resource.allow_delete)
        self.assertFalse(capabilities_resource.allow_list)

    def test_make_capabilities(self):
        capabilities_resource = capabilities.Capabilities(**CAPABILITIES)
        self.assertEqual(
            CAPABILITIES["description"], capabilities_resource.description
        )
        self.assertEqual(
            CAPABILITIES["display_name"], capabilities_resource.display_name
        )
        self.assertEqual(
            CAPABILITIES["driver_version"],
            capabilities_resource.driver_version,
        )
        self.assertEqual(
            CAPABILITIES["namespace"], capabilities_resource.namespace
        )
        self.assertEqual(
            CAPABILITIES["pool_name"], capabilities_resource.pool_name
        )
        self.assertEqual(
            CAPABILITIES["properties"], capabilities_resource.properties
        )
        self.assertEqual(
            CAPABILITIES["replication_targets"],
            capabilities_resource.replication_targets,
        )
        self.assertEqual(
            CAPABILITIES["storage_protocol"],
            capabilities_resource.storage_protocol,
        )
        self.assertEqual(
            CAPABILITIES["vendor_name"], capabilities_resource.vendor_name
        )
        self.assertEqual(
            CAPABILITIES["visibility"], capabilities_resource.visibility
        )
        self.assertEqual(
            CAPABILITIES["volume_backend_name"],
            capabilities_resource.volume_backend_name,
        )
