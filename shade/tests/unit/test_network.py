# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock

import shade
from shade.tests.unit import base


class TestNetwork(base.TestCase):

    def setUp(self):
        super(TestNetwork, self).setUp()
        self.cloud = shade.openstack_cloud(validate=False)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_network(self, mock_neutron):
        self.cloud.create_network("netname")
        mock_neutron.create_network.assert_called_with(
            body=dict(
                network=dict(
                    name='netname',
                    shared=False,
                    admin_state_up=True
                )
            )
        )

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_network_external(self, mock_neutron):
        self.cloud.create_network("netname", external=True)
        mock_neutron.create_network.assert_called_with(
            body=dict(
                network={
                    'name': 'netname',
                    'shared': False,
                    'admin_state_up': True,
                    'router:external': True
                }
            )
        )
