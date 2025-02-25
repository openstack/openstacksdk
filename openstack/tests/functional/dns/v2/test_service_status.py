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

from openstack.tests.functional import base


class TestServiceStatus(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('dns')

        self.service_names = [
            "api",
            "backend",
            "central",
            "mdns",
            "producer",
            "sink",
            "storage",
            "worker",
        ]
        self.service_status = ["UP", "DOWN"]

    def test_service_status(self):
        service_statuses = list(self.operator_cloud.dns.service_statuses())
        if not service_statuses:
            self.skipTest(
                "The Service in Designate System is required for this test"
            )

        names = [f.service_name for f in service_statuses]
        statuses = [f.status for f in service_statuses]

        self.assertTrue(
            all(status in self.service_status for status in statuses)
        )
        self.assertTrue(all(name in self.service_names for name in names))

        # Test that we can fetch a service status
        service_status = self.operator_cloud.dns.get_service_status(
            service_statuses[0]
        )
        self.assertIn(service_status.service_name, self.service_names)
        self.assertIn(service_status.status, self.service_status)
