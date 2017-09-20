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

from shade.tests.unit import base
from shade.tests import fakes


class TestAggregate(base.RequestsMockTestCase):

    def setUp(self):
        super(TestAggregate, self).setUp()
        self.aggregate_name = self.getUniqueString('aggregate')
        self.fake_aggregate = fakes.make_fake_aggregate(1, self.aggregate_name)

    def test_create_aggregate(self):
        create_aggregate = self.fake_aggregate.copy()
        del create_aggregate['metadata']
        del create_aggregate['hosts']

        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-aggregates']),
                 json={'aggregate': create_aggregate},
                 validate=dict(json={
                     'aggregate': {
                         'name': self.aggregate_name,
                         'availability_zone': None,
                     }})),
        ])
        self.op_cloud.create_aggregate(name=self.aggregate_name)

        self.assert_calls()

    def test_create_aggregate_with_az(self):
        availability_zone = 'az1'
        az_aggregate = fakes.make_fake_aggregate(
            1, self.aggregate_name, availability_zone=availability_zone)

        create_aggregate = az_aggregate.copy()
        del create_aggregate['metadata']
        del create_aggregate['hosts']

        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-aggregates']),
                 json={'aggregate': create_aggregate},
                 validate=dict(json={
                     'aggregate': {
                         'name': self.aggregate_name,
                         'availability_zone': availability_zone,
                     }})),
        ])

        self.op_cloud.create_aggregate(
            name=self.aggregate_name, availability_zone=availability_zone)

        self.assert_calls()

    def test_delete_aggregate(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-aggregates']),
                 json={'aggregates': [self.fake_aggregate]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-aggregates', '1'])),
        ])

        self.assertTrue(self.op_cloud.delete_aggregate('1'))

        self.assert_calls()

    def test_update_aggregate_set_az(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-aggregates']),
                 json={'aggregates': [self.fake_aggregate]}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-aggregates', '1']),
                 json={'aggregate': self.fake_aggregate},
                 validate=dict(
                     json={
                         'aggregate': {
                             'availability_zone': 'az',
                         }})),
        ])

        self.op_cloud.update_aggregate(1, availability_zone='az')

        self.assert_calls()

    def test_update_aggregate_unset_az(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-aggregates']),
                 json={'aggregates': [self.fake_aggregate]}),
            dict(method='PUT',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-aggregates', '1']),
                 json={'aggregate': self.fake_aggregate},
                 validate=dict(
                     json={
                         'aggregate': {
                             'availability_zone': None,
                         }})),
        ])

        self.op_cloud.update_aggregate(1, availability_zone=None)

        self.assert_calls()

    def test_set_aggregate_metadata(self):
        metadata = {'key': 'value'}
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-aggregates']),
                 json={'aggregates': [self.fake_aggregate]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['os-aggregates', '1', 'action']),
                 json={'aggregate': self.fake_aggregate},
                 validate=dict(
                     json={'set_metadata': {'metadata': metadata}})),
        ])
        self.op_cloud.set_aggregate_metadata('1', metadata)

        self.assert_calls()

    def test_add_host_to_aggregate(self):
        hostname = 'host1'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-aggregates']),
                 json={'aggregates': [self.fake_aggregate]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['os-aggregates', '1', 'action']),
                 json={'aggregate': self.fake_aggregate},
                 validate=dict(
                     json={'add_host': {'host': hostname}})),
        ])
        self.op_cloud.add_host_to_aggregate('1', hostname)

        self.assert_calls()

    def test_remove_host_from_aggregate(self):
        hostname = 'host1'
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['os-aggregates']),
                 json={'aggregates': [self.fake_aggregate]}),
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['os-aggregates', '1', 'action']),
                 json={'aggregate': self.fake_aggregate},
                 validate=dict(
                     json={'remove_host': {'host': hostname}})),
        ])
        self.op_cloud.remove_host_from_aggregate('1', hostname)

        self.assert_calls()
