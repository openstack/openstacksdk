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

from openstack.placement.v1 import _proxy
from openstack.placement.v1 import resource_class
from openstack.placement.v1 import resource_provider
from openstack.placement.v1 import resource_provider_inventory
from openstack.tests.unit import test_proxy_base as test_proxy_base


class TestPlacementProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestPlacementResourceClass(TestPlacementProxy):
    def test_resource_class_create(self):
        self.verify_create(
            self.proxy.create_resource_class,
            resource_class.ResourceClass,
        )

    def test_resource_class_delete(self):
        self.verify_delete(
            self.proxy.delete_resource_class,
            resource_class.ResourceClass,
            False,
        )

    def test_resource_class_update(self):
        self.verify_update(
            self.proxy.update_resource_class,
            resource_class.ResourceClass,
            False,
        )

    def test_resource_class_get(self):
        self.verify_get(
            self.proxy.get_resource_class,
            resource_class.ResourceClass,
        )

    def test_resource_classes(self):
        self.verify_list(
            self.proxy.resource_classes,
            resource_class.ResourceClass,
        )


class TestPlacementResourceProvider(TestPlacementProxy):
    def test_resource_provider_create(self):
        self.verify_create(
            self.proxy.create_resource_provider,
            resource_provider.ResourceProvider,
        )

    def test_resource_provider_delete(self):
        self.verify_delete(
            self.proxy.delete_resource_provider,
            resource_provider.ResourceProvider,
            False,
        )

    def test_resource_provider_update(self):
        self.verify_update(
            self.proxy.update_resource_provider,
            resource_provider.ResourceProvider,
            False,
        )

    def test_resource_provider_get(self):
        self.verify_get(
            self.proxy.get_resource_provider,
            resource_provider.ResourceProvider,
        )

    def test_resource_providers(self):
        self.verify_list(
            self.proxy.resource_providers,
            resource_provider.ResourceProvider,
        )

    def test_resource_provider_set_aggregates(self):
        self._verify(
            'openstack.placement.v1.resource_provider.ResourceProvider.set_aggregates',
            self.proxy.set_resource_provider_aggregates,
            method_args=['value', 'a', 'b'],
            expected_args=[self.proxy],
            expected_kwargs={'aggregates': ('a', 'b')},
        )

    def test_resource_provider_get_aggregates(self):
        self._verify(
            'openstack.placement.v1.resource_provider.ResourceProvider.fetch_aggregates',
            self.proxy.get_resource_provider_aggregates,
            method_args=['value'],
            expected_args=[self.proxy],
        )


class TestPlacementResourceProviderInventory(TestPlacementProxy):
    def test_resource_provider_inventory_create(self):
        self.verify_create(
            self.proxy.create_resource_provider_inventory,
            resource_provider_inventory.ResourceProviderInventory,
            method_kwargs={
                'resource_provider': 'test_id',
                'resource_class': 'CUSTOM_FOO',
                'total': 20,
            },
            expected_kwargs={
                'resource_provider_id': 'test_id',
                'resource_class': 'CUSTOM_FOO',
                'total': 20,
            },
        )

    def test_resource_provider_inventory_delete(self):
        self.verify_delete(
            self.proxy.delete_resource_provider_inventory,
            resource_provider_inventory.ResourceProviderInventory,
            ignore_missing=False,
            method_kwargs={'resource_provider': 'test_id'},
            expected_kwargs={'resource_provider_id': 'test_id'},
        )

    def test_resource_provider_inventory_update(self):
        self.verify_update(
            self.proxy.update_resource_provider_inventory,
            resource_provider_inventory.ResourceProviderInventory,
            method_kwargs={
                'resource_provider': 'test_id',
                'resource_provider_generation': 1,
            },
            expected_kwargs={
                'resource_provider_id': 'test_id',
                'resource_provider_generation': 1,
            },
        )

    def test_resource_provider_inventory_get(self):
        self.verify_get(
            self.proxy.get_resource_provider_inventory,
            resource_provider_inventory.ResourceProviderInventory,
            method_kwargs={'resource_provider': 'test_id'},
            expected_kwargs={'resource_provider_id': 'test_id'},
        )

    def test_resource_provider_inventories(self):
        self.verify_list(
            self.proxy.resource_provider_inventories,
            resource_provider_inventory.ResourceProviderInventory,
            method_kwargs={'resource_provider': 'test_id'},
            expected_kwargs={'resource_provider_id': 'test_id'},
        )
