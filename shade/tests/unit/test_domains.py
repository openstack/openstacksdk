# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import testtools

import shade
from shade import meta
from shade.tests.unit import base
from shade.tests import fakes


domain_obj = fakes.FakeDomain(
    id='1',
    name='a-domain',
    description='A wonderful keystone domain',
    enabled=True,
)


class TestDomains(base.TestCase):

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_domains(self, mock_keystone):
        self.op_cloud.list_domains()
        self.assertTrue(mock_keystone.domains.list.called)

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_get_domain(self, mock_keystone):
        mock_keystone.domains.get.return_value = domain_obj
        domain = self.op_cloud.get_domain(domain_id='1234')
        self.assertFalse(mock_keystone.domains.list.called)
        self.assertTrue(mock_keystone.domains.get.called)
        self.assertEqual(domain['name'], 'a-domain')

    @mock.patch.object(shade._utils, '_get_entity')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_get_domain_with_name_or_id(self, mock_keystone, mock_get):
        self.op_cloud.get_domain(name_or_id='1234')
        mock_get.assert_called_once_with(mock.ANY,
                                         None, '1234')

    @mock.patch.object(shade._utils, 'normalize_domains')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_create_domain(self, mock_keystone, mock_normalize):
        mock_keystone.domains.create.return_value = domain_obj
        self.op_cloud.create_domain(
            domain_obj.name, domain_obj.description)
        mock_keystone.domains.create.assert_called_once_with(
            name=domain_obj.name, description=domain_obj.description,
            enabled=True)
        mock_normalize.assert_called_once_with([meta.obj_to_dict(domain_obj)])

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_create_domain_exception(self, mock_keystone):
        mock_keystone.domains.create.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Failed to create domain domain_name"
        ):
            self.op_cloud.create_domain('domain_name')

    @mock.patch.object(shade.OperatorCloud, 'update_domain')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_delete_domain(self, mock_keystone, mock_update):
        mock_update.return_value = dict(id='update_domain_id')
        self.op_cloud.delete_domain('domain_id')
        mock_update.assert_called_once_with('domain_id', enabled=False)
        mock_keystone.domains.delete.assert_called_once_with(
            domain='update_domain_id')

    @mock.patch.object(shade.OperatorCloud, 'get_domain')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_delete_domain_name_or_id(self, mock_keystone, mock_get):
        self.op_cloud.update_domain(
            name_or_id='a-domain',
            name='new name',
            description='new description',
            enabled=False)
        mock_get.assert_called_once_with(None, 'a-domain')

    @mock.patch.object(shade.OperatorCloud, 'update_domain')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_delete_domain_exception(self, mock_keystone, mock_update):
        mock_keystone.domains.delete.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Failed to delete domain domain_id"
        ):
            self.op_cloud.delete_domain('domain_id')

    @mock.patch.object(shade._utils, 'normalize_domains')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_update_domain(self, mock_keystone, mock_normalize):
        mock_keystone.domains.update.return_value = domain_obj
        self.op_cloud.update_domain(
            'domain_id',
            name='new name',
            description='new description',
            enabled=False)
        mock_keystone.domains.update.assert_called_once_with(
            domain='domain_id', name='new name',
            description='new description', enabled=False)
        mock_normalize.assert_called_once_with(
            [meta.obj_to_dict(domain_obj)])

    @mock.patch.object(shade.OperatorCloud, 'get_domain')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_update_domain_name_or_id(self, mock_keystone, mock_get):
        self.op_cloud.update_domain(
            name_or_id='a-domain',
            name='new name',
            description='new description',
            enabled=False)
        mock_get.assert_called_once_with(None, 'a-domain')

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_update_domain_exception(self, mock_keystone):
        mock_keystone.domains.update.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Error in updating domain domain_id"
        ):
            self.op_cloud.delete_domain('domain_id')
