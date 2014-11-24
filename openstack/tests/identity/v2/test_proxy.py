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

from openstack.identity.v2 import _proxy
from openstack.tests import test_proxy_base


class TestIdentityProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestIdentityProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_role_create(self):
        self.verify_create('openstack.identity.v2.role.Role.create',
                           self.proxy.create_role)

    def test_role_delete(self):
        self.verify_delete('openstack.identity.v2.role.Role.delete',
                           self.proxy.delete_role)

    def test_role_find(self):
        self.verify_find('openstack.identity.v2.role.Role.find',
                         self.proxy.find_role)

    def test_role_get(self):
        self.verify_get('openstack.identity.v2.role.Role.get',
                        self.proxy.get_role)

    def test_role_list(self):
        self.verify_list('openstack.identity.v2.role.Role.list',
                         self.proxy.list_roles)

    def test_role_update(self):
        self.verify_update('openstack.identity.v2.role.Role.update',
                           self.proxy.update_role)

    def test_tenant_create(self):
        self.verify_create('openstack.identity.v2.tenant.Tenant.create',
                           self.proxy.create_tenant)

    def test_tenant_delete(self):
        self.verify_delete('openstack.identity.v2.tenant.Tenant.delete',
                           self.proxy.delete_tenant)

    def test_tenant_find(self):
        self.verify_find('openstack.identity.v2.tenant.Tenant.find',
                         self.proxy.find_tenant)

    def test_tenant_get(self):
        self.verify_get('openstack.identity.v2.tenant.Tenant.get',
                        self.proxy.get_tenant)

    def test_tenant_list(self):
        self.verify_list('openstack.identity.v2.tenant.Tenant.list',
                         self.proxy.list_tenants)

    def test_tenant_update(self):
        self.verify_update('openstack.identity.v2.tenant.Tenant.update',
                           self.proxy.update_tenant)

    def test_user_create(self):
        self.verify_create('openstack.identity.v2.user.User.create',
                           self.proxy.create_user)

    def test_user_delete(self):
        self.verify_delete('openstack.identity.v2.user.User.delete',
                           self.proxy.delete_user)

    def test_user_find(self):
        self.verify_find('openstack.identity.v2.user.User.find',
                         self.proxy.find_user)

    def test_user_get(self):
        self.verify_get('openstack.identity.v2.user.User.get',
                        self.proxy.get_user)

    def test_user_list(self):
        self.verify_list('openstack.identity.v2.user.User.list',
                         self.proxy.list_users)

    def test_user_update(self):
        self.verify_update('openstack.identity.v2.user.User.update',
                           self.proxy.update_user)
