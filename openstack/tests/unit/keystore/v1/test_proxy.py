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

from openstack.keystore.v1 import _proxy
from openstack.keystore.v1 import container
from openstack.keystore.v1 import order
from openstack.keystore.v1 import secret
from openstack.tests.unit import test_proxy_base


class TestKeystoreProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestKeystoreProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_server_create_attrs(self):
        self.verify_create(self.proxy.create_container, container.Container)

    def test_container_delete(self):
        self.verify_delete2(container.Container,
                            self.proxy.delete_container, False)

    def test_container_delete_ignore(self):
        self.verify_delete2(container.Container,
                            self.proxy.delete_container, True)

    def test_container_find(self):
        self.verify_find('openstack.keystore.v1.container.Container.find',
                         self.proxy.find_container)

    def test_container_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_container,
                         method_args=["resource_or_id"],
                         expected_args=[container.Container, "resource_or_id"])

    def test_containers(self):
        self.verify_list2(self.proxy.containers,
                          expected_args=[container.Container],
                          expected_kwargs={})

    def test_container_update(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_update2('openstack.proxy.BaseProxy._update',
                            self.proxy.update_container,
                            method_args=["resource_or_id"],
                            method_kwargs=kwargs,
                            expected_args=[container.Container,
                                           "resource_or_id"],
                            expected_kwargs=kwargs)

    def test_order_create_attrs(self):
        self.verify_create(self.proxy.create_order, order.Order)

    def test_order_delete(self):
        self.verify_delete2(order.Order, self.proxy.delete_order, False)

    def test_order_delete_ignore(self):
        self.verify_delete2(order.Order, self.proxy.delete_order, True)

    def test_order_find(self):
        self.verify_find('openstack.keystore.v1.order.Order.find',
                         self.proxy.find_order)

    def test_order_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_order,
                         method_args=["resource_or_id"],
                         expected_args=[order.Order, "resource_or_id"])

    def test_orders(self):
        self.verify_list2(self.proxy.orders,
                          expected_args=[order.Order],
                          expected_kwargs={})

    def test_order_update(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_update2('openstack.proxy.BaseProxy._update',
                            self.proxy.update_order,
                            method_args=["resource_or_id"],
                            method_kwargs=kwargs,
                            expected_args=[order.Order, "resource_or_id"],
                            expected_kwargs=kwargs)

    def test_secret_create_attrs(self):
        self.verify_create(self.proxy.create_secret, secret.Secret)

    def test_secret_delete(self):
        self.verify_delete2(secret.Secret, self.proxy.delete_secret, False)

    def test_secret_delete_ignore(self):
        self.verify_delete2(secret.Secret, self.proxy.delete_secret, True)

    def test_secret_find(self):
        self.verify_find('openstack.keystore.v1.secret.Secret.find',
                         self.proxy.find_secret)

    def test_secret_get(self):
        self.verify_get2('openstack.proxy.BaseProxy._get',
                         self.proxy.get_secret,
                         method_args=["resource_or_id"],
                         expected_args=[secret.Secret, "resource_or_id"])

    def test_secrets(self):
        self.verify_list2(self.proxy.secrets,
                          expected_args=[secret.Secret],
                          expected_kwargs={})

    def test_secret_update(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_update2('openstack.proxy.BaseProxy._update',
                            self.proxy.update_secret,
                            method_args=["resource_or_id"],
                            method_kwargs=kwargs,
                            expected_args=[secret.Secret, "resource_or_id"],
                            expected_kwargs=kwargs)
