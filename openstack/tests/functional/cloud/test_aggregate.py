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

"""
test_aggregate
----------------------------------

Functional tests for `shade` aggregate resource.
"""

from openstack.tests.functional.cloud import base


class TestAggregate(base.BaseFunctionalTestCase):

    def test_aggregates(self):
        aggregate_name = self.getUniqueString()
        availability_zone = self.getUniqueString()
        self.addCleanup(self.cleanup, aggregate_name)
        aggregate = self.operator_cloud.create_aggregate(aggregate_name)

        aggregate_ids = [v['id']
                         for v in self.operator_cloud.list_aggregates()]
        self.assertIn(aggregate['id'], aggregate_ids)

        aggregate = self.operator_cloud.update_aggregate(
            aggregate_name,
            availability_zone=availability_zone
        )
        self.assertEqual(availability_zone, aggregate['availability_zone'])

        aggregate = self.operator_cloud.set_aggregate_metadata(
            aggregate_name,
            {'key': 'value'}
        )
        self.assertIn('key', aggregate['metadata'])

        aggregate = self.operator_cloud.set_aggregate_metadata(
            aggregate_name,
            {'key': None}
        )
        self.assertNotIn('key', aggregate['metadata'])

        self.operator_cloud.delete_aggregate(aggregate_name)

    def cleanup(self, aggregate_name):
        aggregate = self.operator_cloud.get_aggregate(aggregate_name)
        if aggregate:
            self.operator_cloud.delete_aggregate(aggregate_name)
