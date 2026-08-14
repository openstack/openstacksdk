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

from openstack.accelerator.v2 import deployable as _deployable
from openstack.tests.functional import base


class TestDeployable(base.BaseFunctionalTest):
    """Test deployables discovered by the fake driver.

    The fake driver creates one device with one deployable on startup,
    so listing and getting deployables should always return results
    without any test setup.
    """

    def setUp(self):
        super().setUp()
        self.require_service('accelerator')

    def test_deployable(self):
        # List
        deployables = list(self.operator_cloud.accelerator.deployables())
        self.assertGreater(
            len(deployables),
            0,
            'no deployables found: is the fake driver enabled?',
        )
        self.assertIsInstance(deployables[0], _deployable.Deployable)

        # Get
        deployable = self.operator_cloud.accelerator.get_deployable(
            deployables[0].id
        )
        self.assertIsInstance(deployable, _deployable.Deployable)
        self.assertEqual(deployables[0].id, deployable.id)
