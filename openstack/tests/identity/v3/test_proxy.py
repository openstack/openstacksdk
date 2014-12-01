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

from openstack.identity.v3 import _proxy
from openstack.tests import test_proxy_base


class TestIdentityProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestIdentityProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_credential_create(self):
        self.verify_create(
            'openstack.identity.v3.credential.Credential.create',
            self.proxy.create_credential)

    def test_credential_delete(self):
        self.verify_delete(
            'openstack.identity.v3.credential.Credential.delete',
            self.proxy.delete_credential)

    def test_credential_find(self):
        self.verify_find('openstack.identity.v3.credential.Credential.find',
                         self.proxy.find_credential)

    def test_credential_get(self):
        self.verify_get('openstack.identity.v3.credential.Credential.get',
                        self.proxy.get_credential)

    def test_credential_list(self):
        self.verify_list('openstack.identity.v3.credential.Credential.list',
                         self.proxy.list_credentials)

    def test_credential_update(self):
        self.verify_update(
            'openstack.identity.v3.credential.Credential.update',
            self.proxy.update_credential)

    def test_domain_create(self):
        self.verify_create('openstack.identity.v3.domain.Domain.create',
                           self.proxy.create_domain)

    def test_domain_delete(self):
        self.verify_delete('openstack.identity.v3.domain.Domain.delete',
                           self.proxy.delete_domain)

    def test_domain_find(self):
        self.verify_find('openstack.identity.v3.domain.Domain.find',
                         self.proxy.find_domain)

    def test_domain_get(self):
        self.verify_get('openstack.identity.v3.domain.Domain.get',
                        self.proxy.get_domain)

    def test_domain_list(self):
        self.verify_list('openstack.identity.v3.domain.Domain.list',
                         self.proxy.list_domains)

    def test_domain_update(self):
        self.verify_update('openstack.identity.v3.domain.Domain.update',
                           self.proxy.update_domain)

    def test_endpoint_create(self):
        self.verify_create('openstack.identity.v3.endpoint.Endpoint.create',
                           self.proxy.create_endpoint)

    def test_endpoint_delete(self):
        self.verify_delete('openstack.identity.v3.endpoint.Endpoint.delete',
                           self.proxy.delete_endpoint)

    def test_endpoint_find(self):
        self.verify_find('openstack.identity.v3.endpoint.Endpoint.find',
                         self.proxy.find_endpoint)

    def test_endpoint_get(self):
        self.verify_get('openstack.identity.v3.endpoint.Endpoint.get',
                        self.proxy.get_endpoint)

    def test_endpoint_list(self):
        self.verify_list('openstack.identity.v3.endpoint.Endpoint.list',
                         self.proxy.list_endpoints)

    def test_endpoint_update(self):
        self.verify_update('openstack.identity.v3.endpoint.Endpoint.update',
                           self.proxy.update_endpoint)

    def test_group_create(self):
        self.verify_create('openstack.identity.v3.group.Group.create',
                           self.proxy.create_group)

    def test_group_delete(self):
        self.verify_delete('openstack.identity.v3.group.Group.delete',
                           self.proxy.delete_group)

    def test_group_find(self):
        self.verify_find('openstack.identity.v3.group.Group.find',
                         self.proxy.find_group)

    def test_group_get(self):
        self.verify_get('openstack.identity.v3.group.Group.get',
                        self.proxy.get_group)

    def test_group_list(self):
        self.verify_list('openstack.identity.v3.group.Group.list',
                         self.proxy.list_groups)

    def test_group_update(self):
        self.verify_update('openstack.identity.v3.group.Group.update',
                           self.proxy.update_group)

    def test_policy_create(self):
        self.verify_create('openstack.identity.v3.policy.Policy.create',
                           self.proxy.create_policy)

    def test_policy_delete(self):
        self.verify_delete('openstack.identity.v3.policy.Policy.delete',
                           self.proxy.delete_policy)

    def test_policy_find(self):
        self.verify_find('openstack.identity.v3.policy.Policy.find',
                         self.proxy.find_policy)

    def test_policy_get(self):
        self.verify_get('openstack.identity.v3.policy.Policy.get',
                        self.proxy.get_policy)

    def test_policy_list(self):
        self.verify_list('openstack.identity.v3.policy.Policy.list',
                         self.proxy.list_policys)

    def test_policy_update(self):
        self.verify_update('openstack.identity.v3.policy.Policy.update',
                           self.proxy.update_policy)

    def test_project_create(self):
        self.verify_create('openstack.identity.v3.project.Project.create',
                           self.proxy.create_project)

    def test_project_delete(self):
        self.verify_delete('openstack.identity.v3.project.Project.delete',
                           self.proxy.delete_project)

    def test_project_find(self):
        self.verify_find('openstack.identity.v3.project.Project.find',
                         self.proxy.find_project)

    def test_project_get(self):
        self.verify_get('openstack.identity.v3.project.Project.get',
                        self.proxy.get_project)

    def test_project_list(self):
        self.verify_list('openstack.identity.v3.project.Project.list',
                         self.proxy.list_projects)

    def test_project_update(self):
        self.verify_update('openstack.identity.v3.project.Project.update',
                           self.proxy.update_project)

    def test_service_create(self):
        self.verify_create('openstack.identity.v3.service.Service.create',
                           self.proxy.create_service)

    def test_service_delete(self):
        self.verify_delete('openstack.identity.v3.service.Service.delete',
                           self.proxy.delete_service)

    def test_service_find(self):
        self.verify_find('openstack.identity.v3.service.Service.find',
                         self.proxy.find_service)

    def test_service_get(self):
        self.verify_get('openstack.identity.v3.service.Service.get',
                        self.proxy.get_service)

    def test_service_list(self):
        self.verify_list('openstack.identity.v3.service.Service.list',
                         self.proxy.list_services)

    def test_service_update(self):
        self.verify_update('openstack.identity.v3.service.Service.update',
                           self.proxy.update_service)

    def test_user_create(self):
        self.verify_create('openstack.identity.v3.user.User.create',
                           self.proxy.create_user)

    def test_user_delete(self):
        self.verify_delete('openstack.identity.v3.user.User.delete',
                           self.proxy.delete_user)

    def test_user_find(self):
        self.verify_find('openstack.identity.v3.user.User.find',
                         self.proxy.find_user)

    def test_user_get(self):
        self.verify_get('openstack.identity.v3.user.User.get',
                        self.proxy.get_user)

    def test_user_list(self):
        self.verify_list('openstack.identity.v3.user.User.list',
                         self.proxy.list_users)

    def test_user_update(self):
        self.verify_update('openstack.identity.v3.user.User.update',
                           self.proxy.update_user)
