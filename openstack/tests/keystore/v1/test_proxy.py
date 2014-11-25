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
from openstack.tests import test_proxy_base


class TestKeystoreProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestKeystoreProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_container_create(self):
        self.verify_create('openstack.keystore.v1.container.Container.create',
                           self.proxy.create_container)

    def test_container_delete(self):
        self.verify_delete('openstack.keystore.v1.container.Container.delete',
                           self.proxy.delete_container)

    def test_container_find(self):
        self.verify_find('openstack.keystore.v1.container.Container.find',
                         self.proxy.find_container)

    def test_container_get(self):
        self.verify_get('openstack.keystore.v1.container.Container.get',
                        self.proxy.get_container)

    def test_container_list(self):
        self.verify_list('openstack.keystore.v1.container.Container.list',
                         self.proxy.list_container)

    def test_container_update(self):
        self.verify_update('openstack.keystore.v1.container.Container.update',
                           self.proxy.update_container)

    def test_order_create(self):
        self.verify_create('openstack.keystore.v1.order.Order.create',
                           self.proxy.create_order)

    def test_order_delete(self):
        self.verify_delete('openstack.keystore.v1.order.Order.delete',
                           self.proxy.delete_order)

    def test_order_find(self):
        self.verify_find('openstack.keystore.v1.order.Order.find',
                         self.proxy.find_order)

    def test_order_get(self):
        self.verify_get('openstack.keystore.v1.order.Order.get',
                        self.proxy.get_order)

    def test_order_list(self):
        self.verify_list('openstack.keystore.v1.order.Order.list',
                         self.proxy.list_order)

    def test_order_update(self):
        self.verify_update('openstack.keystore.v1.order.Order.update',
                           self.proxy.update_order)

    def test_secret_create(self):
        self.verify_create('openstack.keystore.v1.secret.Secret.create',
                           self.proxy.create_secret)

    def test_secret_delete(self):
        self.verify_delete('openstack.keystore.v1.secret.Secret.delete',
                           self.proxy.delete_secret)

    def test_secret_find(self):
        self.verify_find('openstack.keystore.v1.secret.Secret.find',
                         self.proxy.find_secret)

    def test_secret_get(self):
        self.verify_get('openstack.keystore.v1.secret.Secret.get',
                        self.proxy.get_secret)

    def test_secret_list(self):
        self.verify_list('openstack.keystore.v1.secret.Secret.list',
                         self.proxy.list_secret)

    def test_secret_update(self):
        self.verify_update('openstack.keystore.v1.secret.Secret.update',
                           self.proxy.update_secret)
