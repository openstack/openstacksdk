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


import mock

import shade
from shade.tests.unit import base
from shade.tests import fakes


class TestAggregate(base.TestCase):

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_aggregate(self, mock_nova):
        aggregate_name = 'aggr1'
        self.op_cloud.create_aggregate(name=aggregate_name)

        mock_nova.aggregates.create.assert_called_once_with(
            name=aggregate_name, availability_zone=None
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_create_aggregate_with_az(self, mock_nova):
        aggregate_name = 'aggr1'
        availability_zone = 'az1'
        self.op_cloud.create_aggregate(
            name=aggregate_name, availability_zone=availability_zone)

        mock_nova.aggregates.create.assert_called_once_with(
            name=aggregate_name, availability_zone=availability_zone
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_delete_aggregate(self, mock_nova):
        mock_nova.aggregates.list.return_value = [
            fakes.FakeAggregate('1234', 'name')
        ]
        self.assertTrue(self.op_cloud.delete_aggregate('1234'))
        mock_nova.aggregates.list.assert_called_once_with()
        mock_nova.aggregates.delete.assert_called_once_with(
            aggregate='1234'
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_update_aggregate_set_az(self, mock_nova):
        mock_nova.aggregates.list.return_value = [
            fakes.FakeAggregate('1234', 'name')
        ]
        self.op_cloud.update_aggregate('1234', availability_zone='az')
        mock_nova.aggregates.update.assert_called_once_with(
            aggregate='1234',
            values={'availability_zone': 'az'},
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_update_aggregate_unset_az(self, mock_nova):
        mock_nova.aggregates.list.return_value = [
            fakes.FakeAggregate('1234', 'name', availability_zone='az')
        ]
        self.op_cloud.update_aggregate('1234', availability_zone=None)
        mock_nova.aggregates.update.assert_called_once_with(
            aggregate='1234',
            values={'availability_zone': None},
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_set_aggregate_metadata(self, mock_nova):
        metadata = {'key', 'value'}
        mock_nova.aggregates.list.return_value = [
            fakes.FakeAggregate('1234', 'name')
        ]
        self.op_cloud.set_aggregate_metadata('1234', metadata)
        mock_nova.aggregates.set_metadata.assert_called_once_with(
            aggregate='1234',
            metadata=metadata
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_add_host_to_aggregate(self, mock_nova):
        hostname = 'host1'
        mock_nova.aggregates.list.return_value = [
            fakes.FakeAggregate('1234', 'name')
        ]
        self.op_cloud.add_host_to_aggregate('1234', hostname)
        mock_nova.aggregates.add_host.assert_called_once_with(
            aggregate='1234',
            host=hostname
        )

    @mock.patch.object(shade.OpenStackCloud, 'nova_client')
    def test_remove_host_from_aggregate(self, mock_nova):
        hostname = 'host1'
        mock_nova.aggregates.list.return_value = [
            fakes.FakeAggregate('1234', 'name', hosts=[hostname])
        ]
        self.op_cloud.remove_host_from_aggregate('1234', hostname)
        mock_nova.aggregates.remove_host.assert_called_once_with(
            aggregate='1234',
            host=hostname
        )
