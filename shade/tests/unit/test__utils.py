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


from shade import _utils
from shade.tests.unit import base


class TestUtils(base.TestCase):

    def test__filter_list_name_or_id(self):
        el1 = dict(id=100, name='donald')
        el2 = dict(id=200, name='pluto')
        data = [el1, el2]
        ret = _utils._filter_list(data, 'donald', None)
        self.assertEquals([el1], ret)

    def test__filter_list_filter(self):
        el1 = dict(id=100, name='donald', other='duck')
        el2 = dict(id=200, name='donald', other='trump')
        data = [el1, el2]
        ret = _utils._filter_list(data, 'donald', {'other': 'duck'})
        self.assertEquals([el1], ret)

    def test__filter_list_dict1(self):
        el1 = dict(id=100, name='donald', last='duck',
                   other=dict(category='duck'))
        el2 = dict(id=200, name='donald', last='trump',
                   other=dict(category='human'))
        el3 = dict(id=300, name='donald', last='ronald mac',
                   other=dict(category='clown'))
        data = [el1, el2, el3]
        ret = _utils._filter_list(
            data, 'donald', {'other': {'category': 'clown'}})
        self.assertEquals([el3], ret)

    def test__filter_list_dict2(self):
        el1 = dict(id=100, name='donald', last='duck',
                   other=dict(category='duck', financial=dict(status='poor')))
        el2 = dict(id=200, name='donald', last='trump',
                   other=dict(category='human', financial=dict(status='rich')))
        el3 = dict(id=300, name='donald', last='ronald mac',
                   other=dict(category='clown', financial=dict(status='rich')))
        data = [el1, el2, el3]
        ret = _utils._filter_list(
            data, 'donald',
            {'other': {
                'financial': {'status': 'rich'}
                }})
        self.assertEquals([el2, el3], ret)

    def test_normalize_nova_secgroups(self):
        nova_secgroup = dict(
            id='abc123',
            name='nova_secgroup',
            description='A Nova security group',
            rules=[
                dict(id='123', from_port=80, to_port=81, ip_protocol='tcp',
                     ip_range={'cidr': '0.0.0.0/0'}, parent_group_id='xyz123')
            ]
        )

        expected = dict(
            id='abc123',
            name='nova_secgroup',
            description='A Nova security group',
            security_group_rules=[
                dict(id='123', direction='ingress', ethertype='IPv4',
                     port_range_min=80, port_range_max=81, protocol='tcp',
                     remote_ip_prefix='0.0.0.0/0', security_group_id='xyz123')
            ]
        )

        retval = _utils.normalize_nova_secgroups([nova_secgroup])[0]
        self.assertEqual(expected, retval)

    def test_normalize_nova_secgroups_negone_port(self):
        nova_secgroup = dict(
            id='abc123',
            name='nova_secgroup',
            description='A Nova security group with -1 ports',
            rules=[
                dict(id='123', from_port=-1, to_port=-1, ip_protocol='icmp',
                     ip_range={'cidr': '0.0.0.0/0'}, parent_group_id='xyz123')
            ]
        )

        retval = _utils.normalize_nova_secgroups([nova_secgroup])[0]
        self.assertIsNone(retval['security_group_rules'][0]['port_range_min'])
        self.assertIsNone(retval['security_group_rules'][0]['port_range_max'])

    def test_normalize_nova_secgroup_rules(self):
        nova_rules = [
            dict(id='123', from_port=80, to_port=81, ip_protocol='tcp',
                 ip_range={'cidr': '0.0.0.0/0'}, parent_group_id='xyz123')
        ]
        expected = [
            dict(id='123', direction='ingress', ethertype='IPv4',
                 port_range_min=80, port_range_max=81, protocol='tcp',
                 remote_ip_prefix='0.0.0.0/0', security_group_id='xyz123')
        ]
        retval = _utils.normalize_nova_secgroup_rules(nova_rules)
        self.assertEqual(expected, retval)
