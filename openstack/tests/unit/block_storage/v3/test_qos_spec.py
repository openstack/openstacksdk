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

from openstack.block_storage.v3 import qos_spec
from openstack.tests.unit import base

QOS_SPEC = {
    "name": "reliability-spec",
}


class TestSnapshot(base.TestCase):
    def test_basic(self):
        sot = qos_spec.QoSSpec(**QOS_SPEC)
        self.assertEqual("qos_specs", sot.resource_key)
        self.assertEqual("qos_specs", sot.resources_key)
        self.assertEqual("/qos-specs", sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual(
            {
                "project_id": "project_id",
                "limit": "limit",
                "offset": "offset",
                "marker": "marker",
                "sort_dir": "sort_dir",
                "sort_key": "sort_key",
                "sort": "sort",
            },
            sot._query_mapping._mapping,
        )

    def test_create_basic(self):
        sot = qos_spec.QoSSpec(**QOS_SPEC)
        self.assertEqual(QOS_SPEC["name"], sot.name)
