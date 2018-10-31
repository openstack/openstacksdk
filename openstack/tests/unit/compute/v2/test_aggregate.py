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

from openstack.compute.v2 import aggregate

EXAMPLE = {
    "name": "m-family",
    "availability_zone": None,
    "deleted": False,
    "created_at": "2018-07-06T14:58:16.000000",
    "updated_at": None,
    "hosts": ["oscomp-m001", "oscomp-m002", "oscomp-m003"],
    "deleted_at": None,
    "id": 4,
    "metadata": {"type": "public", "family": "m-family"}
}


class TestAggregate(base.TestCase):

    def test_basic(self):
        sot = aggregate.Aggregate()
        self.assertEqual('aggregate', sot.resource_key)
        self.assertEqual('aggregates', sot.resources_key)
        self.assertEqual('/os-aggregates', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = aggregate.Aggregate(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['availability_zone'], sot.availability_zone)
        self.assertEqual(EXAMPLE['deleted'], sot.deleted)
        self.assertEqual(EXAMPLE['hosts'], sot.hosts)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertDictEqual(EXAMPLE['metadata'], sot.metadata)
