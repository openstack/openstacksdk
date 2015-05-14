# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
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

"""
test_floating_ip_pool
----------------------------------

Test floating IP pool resource (managed by nova)
"""

from mock import patch
import os_client_config
from shade import OpenStackCloud
from shade import OpenStackCloudException
from shade.tests.unit import base
from shade.tests.fakes import FakeFloatingIPPool


class TestFloatingIPPool(base.TestCase):
    mock_pools = [
        {'id': 'pool1_id', 'name': 'pool1'},
        {'id': 'pool2_id', 'name': 'pool2'}]

    def setUp(self):
        super(TestFloatingIPPool, self).setUp()
        config = os_client_config.OpenStackConfig()
        self.client = OpenStackCloud(
            cloud_config=config.get_one_cloud(validate=False))

    @patch.object(OpenStackCloud, '_has_nova_extension')
    @patch.object(OpenStackCloud, 'nova_client')
    def test_list_floating_ip_pools(
            self, mock_nova_client, mock__has_nova_extension):
        mock_nova_client.floating_ip_pools.list.return_value = [
            FakeFloatingIPPool(**p) for p in self.mock_pools
        ]
        mock__has_nova_extension.return_value = True

        floating_ip_pools = self.client.list_floating_ip_pools()

        self.assertItemsEqual(floating_ip_pools, self.mock_pools)

    @patch.object(OpenStackCloud, '_has_nova_extension')
    @patch.object(OpenStackCloud, 'nova_client')
    def test_list_floating_ip_pools_exception(
            self, mock_nova_client, mock__has_nova_extension):
        mock_nova_client.floating_ip_pools.list.side_effect = \
            Exception('whatever')
        mock__has_nova_extension.return_value = True

        self.assertRaises(
            OpenStackCloudException, self.client.list_floating_ip_pools)
