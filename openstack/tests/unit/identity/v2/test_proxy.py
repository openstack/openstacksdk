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
from openstack.tests.unit import test_proxy_base


class TestIdentityProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestIdentityProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_role_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_role,
                            method_kwargs=kwargs,
                            expected_args=[role.Role],
                            expected_kwargs=kwargs)

    def test_role_delete(self):
        self.verify_delete2(role.Role, self.proxy.delete_role, False)

    def test_role_delete_ignore(self):
        self.verify_delete2(role.Role, self.proxy.delete_role, True)

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
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_update2('openstack.proxy.BaseProxy._update',
                            self.proxy.update_role,
                            method_args=["resource_or_id"],
                            method_kwargs=kwargs,
                            expected_args=[role.Role, "resource_or_id"],
                            expected_kwargs=kwargs)

    def test_tenant_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_tenant,
                            method_kwargs=kwargs,
                            expected_args=[tenant.Tenant],
                            expected_kwargs=kwargs)

    def test_tenant_delete(self):
        self.verify_delete2(tenant.Tenant, self.proxy.delete_tenant, False)

    def test_tenant_delete_ignore(self):
        self.verify_delete2(tenant.Tenant, self.proxy.delete_tenant, True)

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
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_update2('openstack.proxy.BaseProxy._update',
                            self.proxy.update_tenant,
                            method_args=["resource_or_id"],
                            method_kwargs=kwargs,
                            expected_args=[tenant.Tenant, "resource_or_id"],
                            expected_kwargs=kwargs)

    def test_user_create_attrs(self):
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_create2('openstack.proxy.BaseProxy._create',
                            self.proxy.create_user,
                            method_kwargs=kwargs,
                            expected_args=[user.User],
                            expected_kwargs=kwargs)

    def test_user_delete(self):
        self.verify_delete2(user.User, self.proxy.delete_user, False)

    def test_user_delete_ignore(self):
        self.verify_delete2(user.User, self.proxy.delete_user, True)

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
        kwargs = {"x": 1, "y": 2, "z": 3}
        self.verify_update2('openstack.proxy.BaseProxy._update',
                            self.proxy.update_user,
                            method_args=["resource_or_id"],
                            method_kwargs=kwargs,
                            expected_args=[user.User, "resource_or_id"],
                            expected_kwargs=kwargs)
