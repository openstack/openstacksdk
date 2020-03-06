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
test_magnum_services
--------------------

Functional tests for `shade` services method.
"""

from openstack.tests.functional import base


class TestMagnumServices(base.BaseFunctionalTest):

    def setUp(self):
        super(TestMagnumServices, self).setUp()
        if not self.operator_cloud.has_service(
            'container-infrastructure-management'
        ):
            self.skipTest('Container service not supported by cloud')

    def test_magnum_services(self):
        '''Test magnum services functionality'''

        # Test that we can list services
        services = self.operator_cloud.list_magnum_services()

        self.assertEqual(1, len(services))
        self.assertEqual(services[0]['id'], 1)
        self.assertEqual('up', services[0]['state'])
        self.assertEqual('magnum-conductor', services[0]['binary'])
        self.assertGreater(services[0]['report_count'], 0)
