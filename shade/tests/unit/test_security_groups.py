# -*- coding: utf-8 -*-

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


import copy
import mock

from novaclient import exceptions as nova_exc
from neutronclient.common import exceptions as neutron_exc

import shade
from shade import meta
from shade.tests.unit import base
from shade.tests import fakes


neutron_grp_obj = fakes.FakeSecgroup(
    id='1',
    name='neutron-sec-group',
    description='Test Neutron security group',
    rules=[
        dict(id='1', port_range_min=80, port_range_max=81,
             protocol='tcp', remote_ip_prefix='0.0.0.0/0')
    ]
)


nova_grp_obj = fakes.FakeSecgroup(
    id='2',
    name='nova-sec-group',
    description='Test Nova security group #1',
    rules=[
        dict(id='2', from_port=8000, to_port=8001, ip_protocol='tcp',
             ip_range=dict(cidr='0.0.0.0/0'), parent_group_id=None)
    ]
)


# Neutron returns dicts instead of objects, so the dict versions should
# be used as expected return values from neutron API methods.
neutron_grp_dict = meta.obj_to_dict(neutron_grp_obj)
nova_grp_dict = meta.obj_to_dict(nova_grp_obj)


class TestSecurityGroups(base.TestCase):

    def setUp(self):
        super(TestSecurityGroups, self).setUp()
        self.cloud = shade.openstack_cloud(validate=False)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_list_security_groups_neutron(self, mock_nova, mock_neutron):
        self.cloud.secgroup_source = 'neutron'
        self.cloud.list_security_groups()
        self.assertTrue(mock_neutron.list_security_groups.called)
        self.assertFalse(mock_nova.security_groups.list.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_list_security_groups_nova(self, mock_nova, mock_neutron):
        self.cloud.secgroup_source = 'nova'
        self.cloud.list_security_groups()
        self.assertFalse(mock_neutron.list_security_groups.called)
        self.assertTrue(mock_nova.security_groups.list.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_list_security_groups_none(self, mock_nova, mock_neutron):
        self.cloud.secgroup_source = None
        self.assertRaises(shade.OpenStackCloudUnavailableFeature,
                          self.cloud.list_security_groups)
        self.assertFalse(mock_neutron.list_security_groups.called)
        self.assertFalse(mock_nova.security_groups.list.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_security_group_neutron(self, mock_neutron):
        self.cloud.secgroup_source = 'neutron'
        neutron_return = dict(security_groups=[neutron_grp_dict])
        mock_neutron.list_security_groups.return_value = neutron_return
        self.cloud.delete_security_group('1')
        mock_neutron.delete_security_group.assert_called_once_with(
            security_group='1'
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_security_group_nova(self, mock_nova):
        self.cloud.secgroup_source = 'nova'
        nova_return = [nova_grp_obj]
        mock_nova.security_groups.list.return_value = nova_return
        self.cloud.delete_security_group('2')
        mock_nova.security_groups.delete.assert_called_once_with(
            group='2'
        )

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_security_group_neutron_not_found(self, mock_neutron):
        self.cloud.secgroup_source = 'neutron'
        neutron_return = dict(security_groups=[neutron_grp_dict])
        mock_neutron.list_security_groups.return_value = neutron_return
        self.cloud.delete_security_group('doesNotExist')
        self.assertFalse(mock_neutron.delete_security_group.called)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_security_group_nova_not_found(self, mock_nova):
        self.cloud.secgroup_source = 'nova'
        nova_return = [nova_grp_obj]
        mock_nova.security_groups.list.return_value = nova_return
        self.cloud.delete_security_group('doesNotExist')
        self.assertFalse(mock_nova.security_groups.delete.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_security_group_none(self, mock_nova, mock_neutron):
        self.cloud.secgroup_source = None
        self.assertRaises(shade.OpenStackCloudUnavailableFeature,
                          self.cloud.delete_security_group,
                          'doesNotExist')
        self.assertFalse(mock_neutron.delete_security_group.called)
        self.assertFalse(mock_nova.security_groups.delete.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_security_group_neutron(self, mock_neutron):
        self.cloud.secgroup_source = 'neutron'
        group_name = self.getUniqueString()
        group_desc = 'security group from test_create_security_group_neutron'
        self.cloud.create_security_group(group_name, group_desc)
        mock_neutron.create_security_group.assert_called_once_with(
            body=dict(security_group=dict(name=group_name,
                                          description=group_desc))
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_security_group_nova(self, mock_nova):
        group_name = self.getUniqueString()
        group_desc = 'security group from test_create_security_group_neutron'
        new_group = fakes.FakeSecgroup(id='2',
                                       name=group_name,
                                       description=group_desc,
                                       rules=[])

        mock_nova.security_groups.create.return_value = new_group
        self.cloud.secgroup_source = 'nova'
        r = self.cloud.create_security_group(group_name, group_desc)
        mock_nova.security_groups.create.assert_called_once_with(
            name=group_name, description=group_desc
        )
        self.assertEqual(group_name, r['name'])
        self.assertEqual(group_desc, r['description'])

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_security_group_none(self, mock_nova, mock_neutron):
        self.cloud.secgroup_source = None
        self.assertRaises(shade.OpenStackCloudUnavailableFeature,
                          self.cloud.create_security_group,
                          '', '')
        self.assertFalse(mock_neutron.create_security_group.called)
        self.assertFalse(mock_nova.security_groups.create.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_update_security_group_neutron(self, mock_neutron):
        self.cloud.secgroup_source = 'neutron'
        neutron_return = dict(security_groups=[neutron_grp_dict])
        mock_neutron.list_security_groups.return_value = neutron_return
        self.cloud.update_security_group(neutron_grp_obj.id, name='new_name')
        mock_neutron.update_security_group.assert_called_once_with(
            security_group=neutron_grp_dict['id'],
            body={'security_group': {'name': 'new_name'}}
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_update_security_group_nova(self, mock_nova):
        new_name = self.getUniqueString()
        self.cloud.secgroup_source = 'nova'
        nova_return = [nova_grp_obj]
        update_return = copy.deepcopy(nova_grp_obj)
        update_return.name = new_name
        mock_nova.security_groups.list.return_value = nova_return
        mock_nova.security_groups.update.return_value = update_return
        r = self.cloud.update_security_group(nova_grp_obj.id, name=new_name)
        mock_nova.security_groups.update.assert_called_once_with(
            group=nova_grp_obj.id, name=new_name
        )
        self.assertEqual(r['name'], new_name)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_update_security_group_bad_kwarg(self, mock_nova, mock_neutron):
        self.assertRaises(TypeError,
                          self.cloud.update_security_group,
                          'doesNotExist', bad_arg='')
        self.assertFalse(mock_neutron.create_security_group.called)
        self.assertFalse(mock_nova.security_groups.create.called)

    @mock.patch.object(shade.OpenStackCloud, 'get_security_group')
    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_create_security_group_rule_neutron(self, mock_neutron, mock_get):
        self.cloud.secgroup_source = 'neutron'
        args = dict(
            port_range_min=-1,
            port_range_max=40000,
            protocol='tcp',
            remote_ip_prefix='0.0.0.0/0',
            remote_group_id='456',
            direction='egress',
            ethertype='IPv6'
        )
        mock_get.return_value = {'id': 'abc'}
        self.cloud.create_security_group_rule(secgroup_name_or_id='abc',
                                              **args)

        # For neutron, -1 port should be converted to None
        args['port_range_min'] = None
        args['security_group_id'] = 'abc'

        mock_neutron.create_security_group_rule.assert_called_once_with(
            body={'security_group_rule': args}
        )

    @mock.patch.object(shade.OpenStackCloud, 'get_security_group')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_security_group_rule_nova(self, mock_nova, mock_get):
        self.cloud.secgroup_source = 'nova'

        new_rule = fakes.FakeNovaSecgroupRule(
            id='xyz', from_port=1, to_port=2000, ip_protocol='tcp',
            cidr='1.2.3.4/32')
        mock_nova.security_group_rules.create.return_value = new_rule
        mock_get.return_value = {'id': 'abc'}

        self.cloud.create_security_group_rule(
            'abc', port_range_min=1, port_range_max=2000, protocol='tcp',
            remote_ip_prefix='1.2.3.4/32', remote_group_id='123')

        mock_nova.security_group_rules.create.assert_called_once_with(
            parent_group_id='abc', ip_protocol='tcp', from_port=1,
            to_port=2000, cidr='1.2.3.4/32', group_id='123'
        )

    @mock.patch.object(shade.OpenStackCloud, 'get_security_group')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_security_group_rule_nova_no_ports(self,
                                                      mock_nova, mock_get):
        self.cloud.secgroup_source = 'nova'

        new_rule = fakes.FakeNovaSecgroupRule(
            id='xyz', from_port=1, to_port=65535, ip_protocol='tcp',
            cidr='1.2.3.4/32')
        mock_nova.security_group_rules.create.return_value = new_rule
        mock_get.return_value = {'id': 'abc'}

        self.cloud.create_security_group_rule(
            'abc', protocol='tcp',
            remote_ip_prefix='1.2.3.4/32', remote_group_id='123')

        mock_nova.security_group_rules.create.assert_called_once_with(
            parent_group_id='abc', ip_protocol='tcp', from_port=1,
            to_port=65535, cidr='1.2.3.4/32', group_id='123'
        )

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_security_group_rule_none(self, mock_nova, mock_neutron):
        self.cloud.secgroup_source = None
        self.assertRaises(shade.OpenStackCloudUnavailableFeature,
                          self.cloud.create_security_group_rule,
                          '')
        self.assertFalse(mock_neutron.create_security_group.called)
        self.assertFalse(mock_nova.security_groups.create.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    def test_delete_security_group_rule_neutron(self, mock_neutron):
        self.cloud.secgroup_source = 'neutron'
        r = self.cloud.delete_security_group_rule('xyz')
        mock_neutron.delete_security_group_rule.assert_called_once_with(
            security_group_rule='xyz')
        self.assertTrue(r)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_security_group_rule_nova(self, mock_nova):
        self.cloud.secgroup_source = 'nova'
        r = self.cloud.delete_security_group_rule('xyz')
        mock_nova.security_group_rules.delete.assert_called_once_with(
            rule='xyz')
        self.assertTrue(r)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_security_group_rule_none(self, mock_nova, mock_neutron):
        self.cloud.secgroup_source = None
        self.assertRaises(shade.OpenStackCloudUnavailableFeature,
                          self.cloud.delete_security_group_rule,
                          '')
        self.assertFalse(mock_neutron.create_security_group.called)
        self.assertFalse(mock_nova.security_groups.create.called)

    @mock.patch.object(shade.OpenStackCloud, 'neutron_client')
    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_security_group_rule_not_found(self,
                                                  mock_nova,
                                                  mock_neutron):
        self.cloud.secgroup_source = 'neutron'
        mock_neutron.delete_security_group_rule.side_effect = (
            neutron_exc.NotFound()
        )
        r = self.cloud.delete_security_group('doesNotExist')
        self.assertFalse(r)

        self.cloud.secgroup_source = 'nova'
        mock_neutron.security_group_rules.delete.side_effect = (
            nova_exc.NotFound("uh oh")
        )
        r = self.cloud.delete_security_group('doesNotExist')
        self.assertFalse(r)

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_nova_egress_security_group_rule(self, mock_nova):
        self.cloud.secgroup_source = 'nova'
        mock_nova.security_groups.list.return_value = [nova_grp_obj]
        self.assertRaises(shade.OpenStackCloudException,
                          self.cloud.create_security_group_rule,
                          secgroup_name_or_id='nova-sec-group',
                          direction='egress')
