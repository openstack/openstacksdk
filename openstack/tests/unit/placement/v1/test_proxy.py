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
from openstack.tests.unit import test_proxy_base as test_proxy_base


class TestPlacementProxy(test_proxy_base.TestProxyBase):

    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


# resource classes
class TestPlacementResourceClass:
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


# resource providers
class TestPlacementResourceProvider:
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
