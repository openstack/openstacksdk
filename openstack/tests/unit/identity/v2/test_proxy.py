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
from openstack.identity.v2 import role
from openstack.identity.v2 import tenant
from openstack.identity.v2 import user
from openstack.tests.unit import test_proxy_base2 as test_proxy_base


class TestIdentityProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestIdentityProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_role_create_attrs(self):
        self.verify_create(self.proxy.create_role, role.Role)

    def test_role_delete(self):
        self.verify_delete(self.proxy.delete_role, role.Role, False)

    def test_role_delete_ignore(self):
        self.verify_delete(self.proxy.delete_role, role.Role, True)

    def test_role_find(self):
        self.verify_find(self.proxy.find_role, role.Role)

    def test_role_get(self):
        self.verify_get(self.proxy.get_role, role.Role)

    def test_roles(self):
        self.verify_list(self.proxy.roles, role.Role)

    def test_role_update(self):
        self.verify_update(self.proxy.update_role, role.Role)

    def test_tenant_create_attrs(self):
        self.verify_create(self.proxy.create_tenant, tenant.Tenant)

    def test_tenant_delete(self):
        self.verify_delete(self.proxy.delete_tenant, tenant.Tenant, False)

    def test_tenant_delete_ignore(self):
        self.verify_delete(self.proxy.delete_tenant, tenant.Tenant, True)

    def test_tenant_find(self):
        self.verify_find(self.proxy.find_tenant, tenant.Tenant)

    def test_tenant_get(self):
        self.verify_get(self.proxy.get_tenant, tenant.Tenant)

    def test_tenants(self):
        self.verify_list(self.proxy.tenants, tenant.Tenant, paginated=True)

    def test_tenant_update(self):
        self.verify_update(self.proxy.update_tenant, tenant.Tenant)

    def test_user_create_attrs(self):
        self.verify_create(self.proxy.create_user, user.User)

    def test_user_delete(self):
        self.verify_delete(self.proxy.delete_user, user.User, False)

    def test_user_delete_ignore(self):
        self.verify_delete(self.proxy.delete_user, user.User, True)

    def test_user_find(self):
        self.verify_find(self.proxy.find_user, user.User)

    def test_user_get(self):
        self.verify_get(self.proxy.get_user, user.User)

    def test_users(self):
        self.verify_list(self.proxy.users, user.User)

    def test_user_update(self):
        self.verify_update(self.proxy.update_user, user.User)
