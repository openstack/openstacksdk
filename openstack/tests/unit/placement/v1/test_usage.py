# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from typing import Any

from openstack.placement.v1 import usage
from openstack.tests.unit import base

FAKE: dict[str, Any] = {
    'consumer_type': 'INSTANCE',
    'consumer_count': 5,
    'resources': {
        'VCPU': 2,
        'DISK_GB': 5,
        'MEMORY_MB': 512,
    },
}


class TestUsage(base.TestCase):
    def test_basic(self):
        sot = usage.Usage()
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/usages', sot.base_path)
        self.assertFalse(sot.requires_id)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = usage.Usage(**FAKE)
        self.assertEqual(FAKE['consumer_type'], sot.consumer_type)
        self.assertEqual(FAKE['consumer_count'], sot.consumer_count)
        self.assertEqual(FAKE['resources'], sot.resources)
