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


import shade

from mock import patch
from novaclient import exceptions as nova_exc

from shade import exc
from shade import meta
from shade.tests import fakes
from shade.tests.unit import base


class TestKeypair(base.TestCase):

    def setUp(self):
        super(TestKeypair, self).setUp()
        self.cloud = shade.openstack_cloud(validate=False)

    @patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_keypair(self, mock_nova):
        keyname = 'my_keyname'
        pub_key = 'ssh-rsa BLAH'
        key = fakes.FakeKeypair('keyid', keyname, pub_key)
        mock_nova.keypairs.create.return_value = key

        new_key = self.cloud.create_keypair(keyname, pub_key)
        mock_nova.keypairs.create.assert_called_once_with(
            name=keyname, public_key=pub_key
        )
        self.assertEqual(meta.obj_to_dict(key), new_key)

    @patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_keypair_exception(self, mock_nova):
        mock_nova.keypairs.create.side_effect = Exception()
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.create_keypair, '', '')

    @patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_keypair(self, mock_nova):
        self.assertTrue(self.cloud.delete_keypair('mykey'))
        mock_nova.keypairs.delete.assert_called_once_with(
            key='mykey'
        )

    @patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_keypair_not_found(self, mock_nova):
        mock_nova.keypairs.delete.side_effect = nova_exc.NotFound('')
        self.assertFalse(self.cloud.delete_keypair('invalid'))

    @patch.object(shade.OpenStackCloud, 'nova_client')
    def test_list_keypairs(self, mock_nova):
        self.cloud.list_keypairs()
        mock_nova.keypairs.list.assert_called_once_with()

    @patch.object(shade.OpenStackCloud, 'nova_client')
    def test_list_keypairs_exception(self, mock_nova):
        mock_nova.keypairs.list.side_effect = Exception()
        self.assertRaises(exc.OpenStackCloudException,
                          self.cloud.list_keypairs)
