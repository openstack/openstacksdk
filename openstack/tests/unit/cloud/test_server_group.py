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


import uuid

from openstack.tests.unit import base
from openstack.tests import fakes


class TestServerGroup(base.TestCase):

    def setUp(self):
        super(TestServerGroup, self).setUp()
        self.group_id = uuid.uuid4().hex
        self.group_name = self.getUniqueString('server-group')
        self.policies = ['affinity']
        self.fake_group = fakes.make_fake_server_group(
            self.group_id, self.group_name, self.policies)

    def test_create_server_group(self):

        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-server-groups']),
                 json={'server_group': self.fake_group},
                 validate=dict(
                     json={'server_group': {
                         'name': self.group_name,
                         'policies': self.policies,
                     }})),
        ])

        self.cloud.create_server_group(name=self.group_name,
                                       policies=self.policies)

        self.assert_calls()

    def test_delete_server_group(self):
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-server-groups']),
                 json={'server_groups': [self.fake_group]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['os-server-groups', self.group_id]),
                 json={'server_groups': [self.fake_group]}),
        ])
        self.assertTrue(self.cloud.delete_server_group(self.group_name))

        self.assert_calls()
