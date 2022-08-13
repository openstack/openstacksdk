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

from openstack.compute.v2 import usage
from openstack.tests.unit import base


EXAMPLE = {
    "tenant_id": "781c9299e68d4b7c80ef52712889647f",
    "server_usages": [
        {
            "hours": 79.51840531333333,
            "flavor": "m1.tiny",
            "instance_id": "76638c30-d199-4c2e-8154-7dea963bfe2f",
            "name": "test-server",
            "tenant_id": "781c9299e68d4b7c80ef52712889647f",
            "memory_mb": 512,
            "local_gb": 1,
            "vcpus": 1,
            "started_at": "2022-05-16T10:35:31.000000",
            "ended_at": None,
            "state": "active",
            "uptime": 286266,
        }
    ],
    "total_local_gb_usage": 79.51840531333333,
    "total_vcpus_usage": 79.51840531333333,
    "total_memory_mb_usage": 40713.423520426666,
    "total_hours": 79.51840531333333,
    "start": "2022-04-21T18:06:47.064959",
    "stop": "2022-05-19T18:06:37.259128",
}


class TestUsage(base.TestCase):
    def test_basic(self):
        sot = usage.Usage()
        self.assertEqual('tenant_usage', sot.resource_key)
        self.assertEqual('tenant_usages', sot.resources_key)
        self.assertEqual('/os-simple-tenant-usage', sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = usage.Usage(**EXAMPLE)

        self.assertEqual(EXAMPLE['tenant_id'], sot.project_id)
        self.assertEqual(
            EXAMPLE['total_local_gb_usage'],
            sot.total_local_gb_usage,
        )
        self.assertEqual(EXAMPLE['total_vcpus_usage'], sot.total_vcpus_usage)
        self.assertEqual(
            EXAMPLE['total_memory_mb_usage'],
            sot.total_memory_mb_usage,
        )
        self.assertEqual(EXAMPLE['total_hours'], sot.total_hours)
        self.assertEqual(EXAMPLE['start'], sot.start)
        self.assertEqual(EXAMPLE['stop'], sot.stop)

        # now do the embedded objects
        self.assertIsInstance(sot.server_usages, list)
        self.assertEqual(1, len(sot.server_usages))

        ssot = sot.server_usages[0]
        self.assertIsInstance(ssot, usage.ServerUsage)
        self.assertEqual(EXAMPLE['server_usages'][0]['hours'], ssot.hours)
        self.assertEqual(EXAMPLE['server_usages'][0]['flavor'], ssot.flavor)
        self.assertEqual(
            EXAMPLE['server_usages'][0]['instance_id'], ssot.instance_id
        )
        self.assertEqual(EXAMPLE['server_usages'][0]['name'], ssot.name)
        self.assertEqual(
            EXAMPLE['server_usages'][0]['tenant_id'], ssot.project_id
        )
        self.assertEqual(
            EXAMPLE['server_usages'][0]['memory_mb'], ssot.memory_mb
        )
        self.assertEqual(
            EXAMPLE['server_usages'][0]['local_gb'], ssot.local_gb
        )
        self.assertEqual(EXAMPLE['server_usages'][0]['vcpus'], ssot.vcpus)
        self.assertEqual(
            EXAMPLE['server_usages'][0]['started_at'], ssot.started_at
        )
        self.assertEqual(
            EXAMPLE['server_usages'][0]['ended_at'], ssot.ended_at
        )
        self.assertEqual(EXAMPLE['server_usages'][0]['state'], ssot.state)
        self.assertEqual(EXAMPLE['server_usages'][0]['uptime'], ssot.uptime)
