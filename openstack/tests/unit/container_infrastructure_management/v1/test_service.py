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

from openstack.container_infrastructure_management.v1 import service
from openstack.tests.unit import base

EXAMPLE = {
    "binary": "magnum-conductor",
    "created_at": "2016-08-23T10:52:13+00:00",
    "state": "up",
    "report_count": 2179,
    "updated_at": "2016-08-25T01:13:16+00:00",
    "host": "magnum-manager",
    "disabled_reason": None,
    "id": 1,
}


class TestService(base.TestCase):
    def test_basic(self):
        sot = service.Service()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('mservices', sot.resources_key)
        self.assertEqual('/mservices', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = service.Service(**EXAMPLE)

        self.assertEqual(EXAMPLE['binary'], sot.binary)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['disabled_reason'], sot.disabled_reason)
        self.assertEqual(EXAMPLE['host'], sot.host)
        self.assertEqual(EXAMPLE['report_count'], sot.report_count)
        self.assertEqual(EXAMPLE['state'], sot.state)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
