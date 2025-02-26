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

import openstack.cloud
from openstack import exceptions
from openstack.tests import fakes
from openstack.tests.unit import base


# TODO(mordred): Move id and name to using a getUniqueString() value

neutron_grp_dict = fakes.make_fake_neutron_security_group(
    id='1',
    name='neutron-sec-group',
    description='Test Neutron security group',
    rules=[
        dict(
            id='1',
            port_range_min=80,
            port_range_max=81,
            protocol='tcp',
            remote_ip_prefix='0.0.0.0/0',
        )
    ],
)


nova_grp_dict = fakes.make_fake_nova_security_group(
    id='2',
    name='nova-sec-group',
    description='Test Nova security group #1',
    rules=[
        fakes.make_fake_nova_security_group_rule(
            id='2',
            from_port=8000,
            to_port=8001,
            ip_protocol='tcp',
            cidr='0.0.0.0/0',
        ),
    ],
)


class TestSecurityGroups(base.TestCase):
    def setUp(self):
        super().setUp()
        self.has_neutron = True

        def fake_has_service(*args, **kwargs):
            return self.has_neutron

        self.cloud.has_service = fake_has_service

    def test_list_security_groups_neutron(self):
        project_id = 42
        self.cloud.secgroup_source = 'neutron'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'security-groups'],
                        qs_elements=[f"project_id={project_id}"],
                    ),
                    json={'security_groups': [neutron_grp_dict]},
                )
            ]
        )
        self.cloud.list_security_groups(filters={'project_id': project_id})
        self.assert_calls()

    def test_list_security_groups_nova(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups?project_id=42',
                    json={'security_groups': []},
                ),
            ]
        )
        self.cloud.secgroup_source = 'nova'
        self.has_neutron = False
        self.cloud.list_security_groups(filters={'project_id': 42})

        self.assert_calls()

    def test_list_security_groups_none(self):
        self.cloud.secgroup_source = None
        self.has_neutron = False
        self.assertRaises(
            openstack.cloud.OpenStackCloudUnavailableFeature,
            self.cloud.list_security_groups,
        )

    def test_delete_security_group_neutron(self):
        sg_id = neutron_grp_dict['id']
        self.cloud.secgroup_source = 'neutron'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'security-groups']
                    ),
                    json={'security_groups': [neutron_grp_dict]},
                ),
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'security-groups', f'{sg_id}'],
                    ),
                    status_code=200,
                    json={},
                ),
            ]
        )
        self.assertTrue(self.cloud.delete_security_group('1'))
        self.assert_calls()

    def test_delete_security_group_nova(self):
        self.cloud.secgroup_source = 'nova'
        self.has_neutron = False
        nova_return = [nova_grp_dict]
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups',
                    json={'security_groups': nova_return},
                ),
                dict(
                    method='DELETE',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups/2',
                ),
            ]
        )
        self.cloud.delete_security_group('2')
        self.assert_calls()

    def test_delete_security_group_neutron_not_found(self):
        self.cloud.secgroup_source = 'neutron'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'security-groups']
                    ),
                    json={'security_groups': [neutron_grp_dict]},
                )
            ]
        )
        self.assertFalse(self.cloud.delete_security_group('10'))
        self.assert_calls()

    def test_delete_security_group_nova_not_found(self):
        self.cloud.secgroup_source = 'nova'
        self.has_neutron = False
        nova_return = [nova_grp_dict]
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups',
                    json={'security_groups': nova_return},
                ),
            ]
        )
        self.assertFalse(self.cloud.delete_security_group('doesNotExist'))

    def test_delete_security_group_none(self):
        self.cloud.secgroup_source = None
        self.assertRaises(
            openstack.cloud.OpenStackCloudUnavailableFeature,
            self.cloud.delete_security_group,
            'doesNotExist',
        )

    def test_create_security_group_neutron(self):
        self.cloud.secgroup_source = 'neutron'
        group_name = self.getUniqueString()
        group_desc = self.getUniqueString('description')
        new_group = fakes.make_fake_neutron_security_group(
            id='2', name=group_name, description=group_desc, rules=[]
        )
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'security-groups']
                    ),
                    json={'security_group': new_group},
                    validate=dict(
                        json={
                            'security_group': {
                                'name': group_name,
                                'description': group_desc,
                            }
                        }
                    ),
                )
            ]
        )

        r = self.cloud.create_security_group(group_name, group_desc)
        self.assertEqual(group_name, r['name'])
        self.assertEqual(group_desc, r['description'])
        self.assertEqual(True, r['stateful'])

        self.assert_calls()

    def test_create_security_group_neutron_specific_tenant(self):
        self.cloud.secgroup_source = 'neutron'
        project_id = "861808a93da0484ea1767967c4df8a23"
        group_name = self.getUniqueString()
        group_desc = (
            'security group from '
            'test_create_security_group_neutron_specific_tenant'
        )
        new_group = fakes.make_fake_neutron_security_group(
            id='2',
            name=group_name,
            description=group_desc,
            project_id=project_id,
            rules=[],
        )
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'security-groups']
                    ),
                    json={'security_group': new_group},
                    validate=dict(
                        json={
                            'security_group': {
                                'name': group_name,
                                'description': group_desc,
                                'tenant_id': project_id,
                            }
                        }
                    ),
                )
            ]
        )

        r = self.cloud.create_security_group(
            group_name, group_desc, project_id
        )
        self.assertEqual(group_name, r['name'])
        self.assertEqual(group_desc, r['description'])
        self.assertEqual(project_id, r['tenant_id'])

        self.assert_calls()

    def test_create_security_group_stateless_neutron(self):
        self.cloud.secgroup_source = 'neutron'
        group_name = self.getUniqueString()
        group_desc = self.getUniqueString('description')
        new_group = fakes.make_fake_neutron_security_group(
            id='2',
            name=group_name,
            description=group_desc,
            stateful=False,
            rules=[],
        )
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'security-groups']
                    ),
                    json={'security_group': new_group},
                    validate=dict(
                        json={
                            'security_group': {
                                'name': group_name,
                                'description': group_desc,
                                'stateful': False,
                            }
                        }
                    ),
                )
            ]
        )

        r = self.cloud.create_security_group(
            group_name, group_desc, stateful=False
        )
        self.assertEqual(group_name, r['name'])
        self.assertEqual(group_desc, r['description'])
        self.assertEqual(False, r['stateful'])
        self.assert_calls()

    def test_create_security_group_nova(self):
        group_name = self.getUniqueString()
        self.has_neutron = False
        group_desc = self.getUniqueString('description')
        new_group = fakes.make_fake_nova_security_group(
            id='2', name=group_name, description=group_desc, rules=[]
        )
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups',
                    json={'security_group': new_group},
                    validate=dict(
                        json={
                            'security_group': {
                                'name': group_name,
                                'description': group_desc,
                            }
                        }
                    ),
                ),
            ]
        )

        self.cloud.secgroup_source = 'nova'
        r = self.cloud.create_security_group(group_name, group_desc)
        self.assertEqual(group_name, r['name'])
        self.assertEqual(group_desc, r['description'])

        self.assert_calls()

    def test_create_security_group_none(self):
        self.cloud.secgroup_source = None
        self.has_neutron = False
        self.assertRaises(
            openstack.cloud.OpenStackCloudUnavailableFeature,
            self.cloud.create_security_group,
            '',
            '',
        )

    def test_update_security_group_neutron(self):
        self.cloud.secgroup_source = 'neutron'
        new_name = self.getUniqueString()
        sg_id = neutron_grp_dict['id']
        update_return = neutron_grp_dict.copy()
        update_return['name'] = new_name
        update_return['stateful'] = False
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'security-groups']
                    ),
                    json={'security_groups': [neutron_grp_dict]},
                ),
                dict(
                    method='PUT',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'security-groups', f'{sg_id}'],
                    ),
                    json={'security_group': update_return},
                    validate=dict(
                        json={
                            'security_group': {
                                'name': new_name,
                                'stateful': False,
                            }
                        }
                    ),
                ),
            ]
        )
        r = self.cloud.update_security_group(
            sg_id, name=new_name, stateful=False
        )
        self.assertEqual(r['name'], new_name)
        self.assertEqual(r['stateful'], False)
        self.assert_calls()

    def test_update_security_group_nova(self):
        self.has_neutron = False
        new_name = self.getUniqueString()
        self.cloud.secgroup_source = 'nova'
        nova_return = [nova_grp_dict]
        update_return = nova_grp_dict.copy()
        update_return['name'] = new_name

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups',
                    json={'security_groups': nova_return},
                ),
                dict(
                    method='PUT',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups/2',
                    json={'security_group': update_return},
                ),
            ]
        )

        r = self.cloud.update_security_group(
            nova_grp_dict['id'], name=new_name
        )
        self.assertEqual(r['name'], new_name)
        self.assert_calls()

    def test_update_security_group_bad_kwarg(self):
        self.assertRaises(
            TypeError,
            self.cloud.update_security_group,
            'doesNotExist',
            bad_arg='',
        )

    def test_create_security_group_rule_neutron(self):
        self.cloud.secgroup_source = 'neutron'
        args = dict(
            port_range_min=-1,
            port_range_max=40000,
            protocol='tcp',
            remote_ip_prefix='0.0.0.0/0',
            remote_group_id='456',
            remote_address_group_id='1234-5678',
            direction='egress',
            ethertype='IPv6',
        )
        expected_args = copy.copy(args)
        # For neutron, -1 port should be converted to None
        expected_args['port_range_min'] = None
        expected_args['security_group_id'] = neutron_grp_dict['id']

        expected_new_rule = copy.copy(expected_args)
        expected_new_rule['id'] = '1234'
        expected_new_rule['tenant_id'] = None
        expected_new_rule['project_id'] = expected_new_rule['tenant_id']

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'security-groups']
                    ),
                    json={'security_groups': [neutron_grp_dict]},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'security-group-rules'],
                    ),
                    json={'security_group_rule': expected_new_rule},
                    validate=dict(json={'security_group_rule': expected_args}),
                ),
            ]
        )
        new_rule = self.cloud.create_security_group_rule(
            secgroup_name_or_id=neutron_grp_dict['id'], **args
        ).to_dict(original_names=True)
        # NOTE(gtema): don't check location and not relevant properties
        # in new rule
        new_rule.pop('created_at')
        new_rule.pop('description')
        new_rule.pop('location')
        new_rule.pop('name')
        new_rule.pop('revision_number')
        new_rule.pop('tags')
        new_rule.pop('updated_at')
        new_rule.pop('if-match')
        self.assertEqual(expected_new_rule, new_rule)
        self.assert_calls()

    def test_create_security_group_rule_neutron_specific_tenant(self):
        self.cloud.secgroup_source = 'neutron'
        args = dict(
            port_range_min=-1,
            port_range_max=40000,
            protocol='tcp',
            remote_ip_prefix='0.0.0.0/0',
            remote_group_id='456',
            remote_address_group_id=None,
            direction='egress',
            ethertype='IPv6',
            project_id='861808a93da0484ea1767967c4df8a23',
        )
        expected_args = copy.copy(args)
        # For neutron, -1 port should be converted to None
        expected_args['port_range_min'] = None
        expected_args['security_group_id'] = neutron_grp_dict['id']
        expected_args['tenant_id'] = expected_args['project_id']
        expected_args.pop('project_id')

        expected_new_rule = copy.copy(expected_args)
        expected_new_rule['id'] = '1234'
        expected_new_rule['project_id'] = expected_new_rule['tenant_id']

        # This is not sent in body if == None so should not be in the
        # JSON; see SecurityGroupRule where it is removed.
        expected_args.pop('remote_address_group_id')

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'security-groups']
                    ),
                    json={'security_groups': [neutron_grp_dict]},
                ),
                dict(
                    method='POST',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=['v2.0', 'security-group-rules'],
                    ),
                    json={'security_group_rule': expected_new_rule},
                    validate=dict(json={'security_group_rule': expected_args}),
                ),
            ]
        )
        new_rule = self.cloud.create_security_group_rule(
            secgroup_name_or_id=neutron_grp_dict['id'], **args
        ).to_dict(original_names=True)
        # NOTE(slaweq): don't check location and properties in new rule
        new_rule.pop('created_at')
        new_rule.pop('description')
        new_rule.pop('location')
        new_rule.pop('name')
        new_rule.pop('revision_number')
        new_rule.pop('tags')
        new_rule.pop('updated_at')
        new_rule.pop('if-match')
        self.assertEqual(expected_new_rule, new_rule)
        self.assert_calls()

    def test_create_security_group_rule_nova(self):
        self.has_neutron = False
        self.cloud.secgroup_source = 'nova'

        nova_return = [nova_grp_dict]

        new_rule = fakes.make_fake_nova_security_group_rule(
            id='xyz',
            from_port=1,
            to_port=2000,
            ip_protocol='tcp',
            cidr='1.2.3.4/32',
        )

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups',
                    json={'security_groups': nova_return},
                ),
                dict(
                    method='POST',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-group-rules',
                    json={'security_group_rule': new_rule},
                    validate=dict(
                        json={
                            "security_group_rule": {
                                "from_port": 1,
                                "ip_protocol": "tcp",
                                "to_port": 2000,
                                "parent_group_id": "2",
                                "cidr": "1.2.3.4/32",
                                "group_id": "123",
                            }
                        }
                    ),
                ),
            ]
        )

        self.cloud.create_security_group_rule(
            '2',
            port_range_min=1,
            port_range_max=2000,
            protocol='tcp',
            remote_ip_prefix='1.2.3.4/32',
            remote_group_id='123',
        )

        self.assert_calls()

    def test_create_security_group_rule_nova_no_ports(self):
        self.has_neutron = False
        self.cloud.secgroup_source = 'nova'

        new_rule = fakes.make_fake_nova_security_group_rule(
            id='xyz',
            from_port=1,
            to_port=65535,
            ip_protocol='tcp',
            cidr='1.2.3.4/32',
        )

        nova_return = [nova_grp_dict]

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups',
                    json={'security_groups': nova_return},
                ),
                dict(
                    method='POST',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-group-rules',
                    json={'security_group_rule': new_rule},
                    validate=dict(
                        json={
                            "security_group_rule": {
                                "from_port": 1,
                                "ip_protocol": "tcp",
                                "to_port": 65535,
                                "parent_group_id": "2",
                                "cidr": "1.2.3.4/32",
                                "group_id": "123",
                            }
                        }
                    ),
                ),
            ]
        )

        self.cloud.create_security_group_rule(
            '2',
            protocol='tcp',
            remote_ip_prefix='1.2.3.4/32',
            remote_group_id='123',
        )

        self.assert_calls()

    def test_create_security_group_rule_none(self):
        self.has_neutron = False
        self.cloud.secgroup_source = None
        self.assertRaises(
            openstack.cloud.OpenStackCloudUnavailableFeature,
            self.cloud.create_security_group_rule,
            '',
        )

    def test_delete_security_group_rule_neutron(self):
        rule_id = "xyz"
        self.cloud.secgroup_source = 'neutron'
        self.register_uris(
            [
                dict(
                    method='DELETE',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=[
                            'v2.0',
                            'security-group-rules',
                            f'{rule_id}',
                        ],
                    ),
                    json={},
                )
            ]
        )
        self.assertTrue(self.cloud.delete_security_group_rule(rule_id))
        self.assert_calls()

    def test_delete_security_group_rule_nova(self):
        self.has_neutron = False
        self.cloud.secgroup_source = 'nova'
        self.register_uris(
            [
                dict(
                    method='DELETE',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-group-rules/xyz',
                ),
            ]
        )
        r = self.cloud.delete_security_group_rule('xyz')
        self.assertTrue(r)
        self.assert_calls()

    def test_delete_security_group_rule_none(self):
        self.has_neutron = False
        self.cloud.secgroup_source = None
        self.assertRaises(
            openstack.cloud.OpenStackCloudUnavailableFeature,
            self.cloud.delete_security_group_rule,
            '',
        )

    def test_delete_security_group_rule_not_found(self):
        rule_id = "doesNotExist"
        self.cloud.secgroup_source = 'neutron'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'security-groups']
                    ),
                    json={'security_groups': [neutron_grp_dict]},
                )
            ]
        )
        self.assertFalse(self.cloud.delete_security_group(rule_id))
        self.assert_calls()

    def test_delete_security_group_rule_not_found_nova(self):
        self.has_neutron = False
        self.cloud.secgroup_source = 'nova'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups',
                    json={'security_groups': [nova_grp_dict]},
                ),
            ]
        )
        r = self.cloud.delete_security_group('doesNotExist')
        self.assertFalse(r)

        self.assert_calls()

    def test_nova_egress_security_group_rule(self):
        self.has_neutron = False
        self.cloud.secgroup_source = 'nova'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups',
                    json={'security_groups': [nova_grp_dict]},
                ),
            ]
        )
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.create_security_group_rule,
            secgroup_name_or_id='nova-sec-group',
            direction='egress',
        )

        self.assert_calls()

    def test_list_server_security_groups_nova(self):
        self.has_neutron = False

        server = fakes.make_fake_server('1234', 'server-name', 'ACTIVE')

        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', server['id']]
                    ),
                    json=server,
                ),
                dict(
                    method='GET',
                    uri='{endpoint}/servers/{id}/os-security-groups'.format(
                        endpoint=fakes.COMPUTE_ENDPOINT, id=server['id']
                    ),
                    json={'security_groups': [nova_grp_dict]},
                ),
            ]
        )
        groups = self.cloud.list_server_security_groups(server)
        self.assertEqual(
            groups[0]['rules'][0]['ip_range']['cidr'],
            nova_grp_dict['rules'][0]['ip_range']['cidr'],
        )

        self.assert_calls()

    def test_list_server_security_groups_bad_source(self):
        self.has_neutron = False
        self.cloud.secgroup_source = 'invalid'
        server = dict(id='server_id')
        ret = self.cloud.list_server_security_groups(server)
        self.assertEqual([], ret)

    def test_add_security_group_to_server_nova(self):
        self.has_neutron = False
        self.cloud.secgroup_source = 'nova'

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups',
                    json={'security_groups': [nova_grp_dict]},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri='{}/servers/{}/action'.format(
                        fakes.COMPUTE_ENDPOINT, '1234'
                    ),
                    validate=dict(
                        json={'addSecurityGroup': {'name': 'nova-sec-group'}}
                    ),
                    status_code=202,
                ),
            ]
        )

        ret = self.cloud.add_server_security_groups(
            dict(id='1234'), 'nova-sec-group'
        )

        self.assertTrue(ret)

        self.assert_calls()

    def test_add_security_group_to_server_neutron(self):
        # fake to get server by name, server-name must match
        fake_server = fakes.make_fake_server('1234', 'server-name', 'ACTIVE')

        # use neutron for secgroup list and return an existing fake
        self.cloud.secgroup_source = 'neutron'

        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'server-name'],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'detail'],
                        qs_elements=['name=server-name'],
                    ),
                    json={'servers': [fake_server]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'security-groups']
                    ),
                    json={'security_groups': [neutron_grp_dict]},
                ),
                dict(
                    method='POST',
                    uri='{}/servers/{}/action'.format(
                        fakes.COMPUTE_ENDPOINT, '1234'
                    ),
                    validate=dict(
                        json={
                            'addSecurityGroup': {'name': 'neutron-sec-group'}
                        }
                    ),
                    status_code=202,
                ),
            ]
        )

        self.assertTrue(
            self.cloud.add_server_security_groups(
                'server-name', 'neutron-sec-group'
            )
        )
        self.assert_calls()

    def test_remove_security_group_from_server_nova(self):
        self.has_neutron = False
        self.cloud.secgroup_source = 'nova'

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups',
                    json={'security_groups': [nova_grp_dict]},
                ),
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='POST',
                    uri='{}/servers/{}/action'.format(
                        fakes.COMPUTE_ENDPOINT, '1234'
                    ),
                    validate=dict(
                        json={
                            'removeSecurityGroup': {'name': 'nova-sec-group'}
                        }
                    ),
                ),
            ]
        )

        ret = self.cloud.remove_server_security_groups(
            dict(id='1234'), 'nova-sec-group'
        )
        self.assertTrue(ret)

        self.assert_calls()

    def test_remove_security_group_from_server_neutron(self):
        # fake to get server by name, server-name must match
        fake_server = fakes.make_fake_server('1234', 'server-name', 'ACTIVE')

        # use neutron for secgroup list and return an existing fake
        self.cloud.secgroup_source = 'neutron'

        validate = {'removeSecurityGroup': {'name': 'neutron-sec-group'}}
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'server-name'],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'detail'],
                        qs_elements=['name=server-name'],
                    ),
                    json={'servers': [fake_server]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'security-groups']
                    ),
                    json={'security_groups': [neutron_grp_dict]},
                ),
                dict(
                    method='POST',
                    uri='{}/servers/{}/action'.format(
                        fakes.COMPUTE_ENDPOINT, '1234'
                    ),
                    validate=dict(json=validate),
                ),
            ]
        )

        self.assertTrue(
            self.cloud.remove_server_security_groups(
                'server-name', 'neutron-sec-group'
            )
        )
        self.assert_calls()

    def test_add_bad_security_group_to_server_nova(self):
        # fake to get server by name, server-name must match
        fake_server = fakes.make_fake_server('1234', 'server-name', 'ACTIVE')

        # use nova for secgroup list and return an existing fake
        self.has_neutron = False
        self.cloud.secgroup_source = 'nova'
        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'server-name'],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'detail'],
                        qs_elements=['name=server-name'],
                    ),
                    json={'servers': [fake_server]},
                ),
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-security-groups',
                    json={'security_groups': [nova_grp_dict]},
                ),
            ]
        )

        ret = self.cloud.add_server_security_groups(
            'server-name', 'unknown-sec-group'
        )
        self.assertFalse(ret)

        self.assert_calls()

    def test_add_bad_security_group_to_server_neutron(self):
        # fake to get server by name, server-name must match
        fake_server = fakes.make_fake_server('1234', 'server-name', 'ACTIVE')

        # use neutron for secgroup list and return an existing fake
        self.cloud.secgroup_source = 'neutron'

        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'server-name'],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'detail'],
                        qs_elements=['name=server-name'],
                    ),
                    json={'servers': [fake_server]},
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network', 'public', append=['v2.0', 'security-groups']
                    ),
                    json={'security_groups': [neutron_grp_dict]},
                ),
            ]
        )
        self.assertFalse(
            self.cloud.add_server_security_groups(
                'server-name', 'unknown-sec-group'
            )
        )
        self.assert_calls()

    def test_add_security_group_to_bad_server(self):
        # fake to get server by name, server-name must match
        fake_server = fakes.make_fake_server('1234', 'server-name', 'ACTIVE')

        print(
            self.get_mock_url(
                'compute',
                'public',
                append=['servers', 'unknown-server-name'],
                base_url_append='v2.1',
            )
        )

        self.register_uris(
            [
                self.get_nova_discovery_mock_dict(),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'unknown-server-name'],
                    ),
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'detail'],
                        qs_elements=['name=unknown-server-name'],
                    ),
                    json={'servers': [fake_server]},
                ),
            ]
        )

        ret = self.cloud.add_server_security_groups(
            'unknown-server-name', 'nova-sec-group'
        )
        self.assertFalse(ret)

        self.assert_calls()

    def test_get_security_group_by_id_neutron(self):
        self.cloud.secgroup_source = 'neutron'
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'network',
                        'public',
                        append=[
                            'v2.0',
                            'security-groups',
                            neutron_grp_dict['id'],
                        ],
                    ),
                    json={'security_group': neutron_grp_dict},
                )
            ]
        )
        ret_sg = self.cloud.get_security_group_by_id(neutron_grp_dict['id'])
        self.assertEqual(neutron_grp_dict['id'], ret_sg['id'])
        self.assertEqual(neutron_grp_dict['name'], ret_sg['name'])
        self.assertEqual(
            neutron_grp_dict['description'], ret_sg['description']
        )
        self.assertEqual(neutron_grp_dict['stateful'], ret_sg['stateful'])
        self.assert_calls()

    def test_get_security_group_by_id_nova(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='{endpoint}/os-security-groups/{id}'.format(
                        endpoint=fakes.COMPUTE_ENDPOINT, id=nova_grp_dict['id']
                    ),
                    json={'security_group': nova_grp_dict},
                ),
            ]
        )
        self.cloud.secgroup_source = 'nova'
        self.has_neutron = False
        ret_sg = self.cloud.get_security_group_by_id(nova_grp_dict['id'])
        self.assertEqual(nova_grp_dict['id'], ret_sg['id'])
        self.assertEqual(nova_grp_dict['name'], ret_sg['name'])
        self.assert_calls()

    def test_normalize_secgroups(self):
        nova_secgroup = dict(
            id='abc123',
            name='nova_secgroup',
            description='A Nova security group',
            rules=[
                dict(
                    id='123',
                    from_port=80,
                    to_port=81,
                    ip_protocol='tcp',
                    ip_range={'cidr': '0.0.0.0/0'},
                    parent_group_id='xyz123',
                )
            ],
        )
        expected = dict(
            id='abc123',
            name='nova_secgroup',
            description='A Nova security group',
            project_id='',
            tenant_id='',
            properties={},
            location=dict(
                region_name='RegionOne',
                zone=None,
                project=dict(
                    domain_name='default',
                    id='1c36b64c840a42cd9e9b931a369337f0',
                    domain_id=None,
                    name='admin',
                ),
                cloud='_test_cloud_',
            ),
            security_group_rules=[
                dict(
                    id='123',
                    direction='ingress',
                    ethertype='IPv4',
                    port_range_min=80,
                    port_range_max=81,
                    protocol='tcp',
                    remote_ip_prefix='0.0.0.0/0',
                    security_group_id='xyz123',
                    project_id='',
                    tenant_id='',
                    properties={},
                    remote_group_id=None,
                    location=dict(
                        region_name='RegionOne',
                        zone=None,
                        project=dict(
                            domain_name='default',
                            id='1c36b64c840a42cd9e9b931a369337f0',
                            domain_id=None,
                            name='admin',
                        ),
                        cloud='_test_cloud_',
                    ),
                )
            ],
        )
        # Set secgroup source to nova for this test as stateful parameter
        # is only valid for neutron security groups.
        self.cloud.secgroup_source = 'nova'
        retval = self.cloud._normalize_secgroup(nova_secgroup)
        self.cloud.secgroup_source = 'neutron'
        self.assertEqual(expected, retval)

    def test_normalize_secgroups_negone_port(self):
        nova_secgroup = dict(
            id='abc123',
            name='nova_secgroup',
            description='A Nova security group with -1 ports',
            rules=[
                dict(
                    id='123',
                    from_port=-1,
                    to_port=-1,
                    ip_protocol='icmp',
                    ip_range={'cidr': '0.0.0.0/0'},
                    parent_group_id='xyz123',
                )
            ],
        )
        retval = self.cloud._normalize_secgroup(nova_secgroup)
        self.assertIsNone(retval['security_group_rules'][0]['port_range_min'])
        self.assertIsNone(retval['security_group_rules'][0]['port_range_max'])

    def test_normalize_secgroup_rules(self):
        nova_rules = [
            dict(
                id='123',
                from_port=80,
                to_port=81,
                ip_protocol='tcp',
                ip_range={'cidr': '0.0.0.0/0'},
                parent_group_id='xyz123',
            )
        ]
        expected = [
            dict(
                id='123',
                direction='ingress',
                ethertype='IPv4',
                port_range_min=80,
                port_range_max=81,
                protocol='tcp',
                remote_ip_prefix='0.0.0.0/0',
                security_group_id='xyz123',
                tenant_id='',
                project_id='',
                remote_group_id=None,
                properties={},
                location=dict(
                    region_name='RegionOne',
                    zone=None,
                    project=dict(
                        domain_name='default',
                        id='1c36b64c840a42cd9e9b931a369337f0',
                        domain_id=None,
                        name='admin',
                    ),
                    cloud='_test_cloud_',
                ),
            )
        ]
        retval = self.cloud._normalize_secgroup_rules(nova_rules)
        self.assertEqual(expected, retval)
