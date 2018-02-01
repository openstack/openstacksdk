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

from openstack.key_manager.v1 import _proxy
from openstack.key_manager.v1 import container
from openstack.key_manager.v1 import order
from openstack.key_manager.v1 import secret
from openstack.tests.unit import test_proxy_base


class TestKeyManagerProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestKeyManagerProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_server_create_attrs(self):
        self.verify_create(self.proxy.create_container, container.Container)

    def test_container_delete(self):
        self.verify_delete(self.proxy.delete_container,
                           container.Container, False)

    def test_container_delete_ignore(self):
        self.verify_delete(self.proxy.delete_container,
                           container.Container, True)

    def test_container_find(self):
        self.verify_find(self.proxy.find_container, container.Container)

    def test_container_get(self):
        self.verify_get(self.proxy.get_container, container.Container)

    def test_containers(self):
        self.verify_list(self.proxy.containers, container.Container,
                         paginated=False)

    def test_container_update(self):
        self.verify_update(self.proxy.update_container, container.Container)

    def test_order_create_attrs(self):
        self.verify_create(self.proxy.create_order, order.Order)

    def test_order_delete(self):
        self.verify_delete(self.proxy.delete_order, order.Order, False)

    def test_order_delete_ignore(self):
        self.verify_delete(self.proxy.delete_order, order.Order, True)

    def test_order_find(self):
        self.verify_find(self.proxy.find_order, order.Order)

    def test_order_get(self):
        self.verify_get(self.proxy.get_order, order.Order)

    def test_orders(self):
        self.verify_list(self.proxy.orders, order.Order, paginated=False)

    def test_order_update(self):
        self.verify_update(self.proxy.update_order, order.Order)

    def test_secret_create_attrs(self):
        self.verify_create(self.proxy.create_secret, secret.Secret)

    def test_secret_delete(self):
        self.verify_delete(self.proxy.delete_secret, secret.Secret, False)

    def test_secret_delete_ignore(self):
        self.verify_delete(self.proxy.delete_secret, secret.Secret, True)

    def test_secret_find(self):
        self.verify_find(self.proxy.find_secret, secret.Secret)

    def test_secret_get(self):
        self.verify_get(self.proxy.get_secret, secret.Secret)
        self.verify_get_overrided(
            self.proxy, secret.Secret,
            'openstack.key_manager.v1.secret.Secret')

    def test_secrets(self):
        self.verify_list(self.proxy.secrets, secret.Secret, paginated=False)

    def test_secret_update(self):
        self.verify_update(self.proxy.update_secret, secret.Secret)
