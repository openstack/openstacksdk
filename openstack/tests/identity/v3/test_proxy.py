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

    def test_credential(self):
        self.verify_create(
            'openstack.identity.v3.credential.Credential.create',
            self.proxy.create_credential
        )
        self.verify_delete(
            'openstack.identity.v3.credential.Credential.delete',
            self.proxy.delete_credential
        )
        self.verify_find('openstack.identity.v3.credential.Credential.find',
                         self.proxy.find_credential)
        self.verify_get('openstack.identity.v3.credential.Credential.get',
                        self.proxy.get_credential)
        self.verify_list('openstack.identity.v3.credential.Credential.list',
                         self.proxy.list_credential)
        self.verify_update(
            'openstack.identity.v3.credential.Credential.update',
            self.proxy.update_credential
        )

    def test_domain(self):
        self.verify_create('openstack.identity.v3.domain.Domain.create',
                           self.proxy.create_domain)
        self.verify_delete('openstack.identity.v3.domain.Domain.delete',
                           self.proxy.delete_domain)
        self.verify_find('openstack.identity.v3.domain.Domain.find',
                         self.proxy.find_domain)
        self.verify_get('openstack.identity.v3.domain.Domain.get',
                        self.proxy.get_domain)
        self.verify_list('openstack.identity.v3.domain.Domain.list',
                         self.proxy.list_domain)
        self.verify_update('openstack.identity.v3.domain.Domain.update',
                           self.proxy.update_domain)

    def test_endpoint(self):
        self.verify_create('openstack.identity.v3.endpoint.Endpoint.create',
                           self.proxy.create_endpoint)
        self.verify_delete('openstack.identity.v3.endpoint.Endpoint.delete',
                           self.proxy.delete_endpoint)
        self.verify_find('openstack.identity.v3.endpoint.Endpoint.find',
                         self.proxy.find_endpoint)
        self.verify_get('openstack.identity.v3.endpoint.Endpoint.get',
                        self.proxy.get_endpoint)
        self.verify_list('openstack.identity.v3.endpoint.Endpoint.list',
                         self.proxy.list_endpoint)
        self.verify_update('openstack.identity.v3.endpoint.Endpoint.update',
                           self.proxy.update_endpoint)

    def test_group(self):
        self.verify_create('openstack.identity.v3.group.Group.create',
                           self.proxy.create_group)
        self.verify_delete('openstack.identity.v3.group.Group.delete',
                           self.proxy.delete_group)
        self.verify_find('openstack.identity.v3.group.Group.find',
                         self.proxy.find_group)
        self.verify_get('openstack.identity.v3.group.Group.get',
                        self.proxy.get_group)
        self.verify_list('openstack.identity.v3.group.Group.list',
                         self.proxy.list_group)
        self.verify_update('openstack.identity.v3.group.Group.update',
                           self.proxy.update_group)

    def test_policy(self):
        self.verify_create('openstack.identity.v3.policy.Policy.create',
                           self.proxy.create_policy)
        self.verify_delete('openstack.identity.v3.policy.Policy.delete',
                           self.proxy.delete_policy)
        self.verify_find('openstack.identity.v3.policy.Policy.find',
                         self.proxy.find_policy)
        self.verify_get('openstack.identity.v3.policy.Policy.get',
                        self.proxy.get_policy)
        self.verify_list('openstack.identity.v3.policy.Policy.list',
                         self.proxy.list_policy)
        self.verify_update('openstack.identity.v3.policy.Policy.update',
                           self.proxy.update_policy)

    def test_project(self):
        self.verify_create('openstack.identity.v3.project.Project.create',
                           self.proxy.create_project)
        self.verify_delete('openstack.identity.v3.project.Project.delete',
                           self.proxy.delete_project)
        self.verify_find('openstack.identity.v3.project.Project.find',
                         self.proxy.find_project)
        self.verify_get('openstack.identity.v3.project.Project.get',
                        self.proxy.get_project)
        self.verify_list('openstack.identity.v3.project.Project.list',
                         self.proxy.list_project)
        self.verify_update('openstack.identity.v3.project.Project.update',
                           self.proxy.update_project)

    def test_service(self):
        self.verify_create('openstack.identity.v3.service.Service.create',
                           self.proxy.create_service)
        self.verify_delete('openstack.identity.v3.service.Service.delete',
                           self.proxy.delete_service)
        self.verify_find('openstack.identity.v3.service.Service.find',
                         self.proxy.find_service)
        self.verify_get('openstack.identity.v3.service.Service.get',
                        self.proxy.get_service)
        self.verify_list('openstack.identity.v3.service.Service.list',
                         self.proxy.list_service)
        self.verify_update('openstack.identity.v3.service.Service.update',
                           self.proxy.update_service)

    def test_user(self):
        self.verify_create('openstack.identity.v3.user.User.create',
                           self.proxy.create_user)
        self.verify_delete('openstack.identity.v3.user.User.delete',
                           self.proxy.delete_user)
        self.verify_find('openstack.identity.v3.user.User.find',
                         self.proxy.find_user)
        self.verify_get('openstack.identity.v3.user.User.get',
                        self.proxy.get_user)
        self.verify_list('openstack.identity.v3.user.User.list',
                         self.proxy.list_user)
        self.verify_update('openstack.identity.v3.user.User.update',
                           self.proxy.update_user)
