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
from openstack.identity.v3 import credential
from openstack.identity.v3 import domain
from openstack.identity.v3 import endpoint
from openstack.identity.v3 import group
from openstack.identity.v3 import policy
from openstack.identity.v3 import project
from openstack.identity.v3 import region
from openstack.identity.v3 import role
from openstack.identity.v3 import service
from openstack.identity.v3 import trust
from openstack.identity.v3 import user
from openstack.tests.unit import test_proxy_base2


class TestIdentityProxy(test_proxy_base2.TestProxyBase):
    def setUp(self):
        super(TestIdentityProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_credential_create_attrs(self):
        self.verify_create(self.proxy.create_credential,
                           credential.Credential)

    def test_credential_delete(self):
        self.verify_delete(self.proxy.delete_credential,
                           credential.Credential, False)

    def test_credential_delete_ignore(self):
        self.verify_delete(self.proxy.delete_credential,
                           credential.Credential, True)

    def test_credential_find(self):
        self.verify_find(self.proxy.find_credential, credential.Credential)

    def test_credential_get(self):
        self.verify_get(self.proxy.get_credential, credential.Credential)

    def test_credentials(self):
        self.verify_list(self.proxy.credentials, credential.Credential,
                         paginated=False)

    def test_credential_update(self):
        self.verify_update(self.proxy.update_credential, credential.Credential)

    def test_domain_create_attrs(self):
        self.verify_create(self.proxy.create_domain, domain.Domain)

    def test_domain_delete(self):
        self.verify_delete(self.proxy.delete_domain, domain.Domain, False)

    def test_domain_delete_ignore(self):
        self.verify_delete(self.proxy.delete_domain, domain.Domain, True)

    def test_domain_find(self):
        self.verify_find(self.proxy.find_domain, domain.Domain)

    def test_domain_get(self):
        self.verify_get(self.proxy.get_domain, domain.Domain)

    def test_domains(self):
        self.verify_list(self.proxy.domains, domain.Domain, paginated=False)

    def test_domain_update(self):
        self.verify_update(self.proxy.update_domain, domain.Domain)

    def test_endpoint_create_attrs(self):
        self.verify_create(self.proxy.create_endpoint, endpoint.Endpoint)

    def test_endpoint_delete(self):
        self.verify_delete(self.proxy.delete_endpoint,
                           endpoint.Endpoint, False)

    def test_endpoint_delete_ignore(self):
        self.verify_delete(self.proxy.delete_endpoint,
                           endpoint.Endpoint, True)

    def test_endpoint_find(self):
        self.verify_find(self.proxy.find_endpoint, endpoint.Endpoint)

    def test_endpoint_get(self):
        self.verify_get(self.proxy.get_endpoint, endpoint.Endpoint)

    def test_endpoints(self):
        self.verify_list(self.proxy.endpoints, endpoint.Endpoint,
                         paginated=False)

    def test_endpoint_update(self):
        self.verify_update(self.proxy.update_endpoint, endpoint.Endpoint)

    def test_group_create_attrs(self):
        self.verify_create(self.proxy.create_group, group.Group)

    def test_group_delete(self):
        self.verify_delete(self.proxy.delete_group, group.Group, False)

    def test_group_delete_ignore(self):
        self.verify_delete(self.proxy.delete_group, group.Group, True)

    def test_group_find(self):
        self.verify_find(self.proxy.find_group, group.Group)

    def test_group_get(self):
        self.verify_get(self.proxy.get_group, group.Group)

    def test_groups(self):
        self.verify_list(self.proxy.groups, group.Group, paginated=False)

    def test_group_update(self):
        self.verify_update(self.proxy.update_group, group.Group)

    def test_policy_create_attrs(self):
        self.verify_create(self.proxy.create_policy, policy.Policy)

    def test_policy_delete(self):
        self.verify_delete(self.proxy.delete_policy, policy.Policy, False)

    def test_policy_delete_ignore(self):
        self.verify_delete(self.proxy.delete_policy, policy.Policy, True)

    def test_policy_find(self):
        self.verify_find(self.proxy.find_policy, policy.Policy)

    def test_policy_get(self):
        self.verify_get(self.proxy.get_policy, policy.Policy)

    def test_policies(self):
        self.verify_list(self.proxy.policies, policy.Policy, paginated=False)

    def test_policy_update(self):
        self.verify_update(self.proxy.update_policy, policy.Policy)

    def test_project_create_attrs(self):
        self.verify_create(self.proxy.create_project, project.Project)

    def test_project_delete(self):
        self.verify_delete(self.proxy.delete_project, project.Project, False)

    def test_project_delete_ignore(self):
        self.verify_delete(self.proxy.delete_project, project.Project, True)

    def test_project_find(self):
        self.verify_find(self.proxy.find_project, project.Project)

    def test_project_get(self):
        self.verify_get(self.proxy.get_project, project.Project)

    def test_projects(self):
        self.verify_list(self.proxy.projects, project.Project, paginated=False)

    def test_project_update(self):
        self.verify_update(self.proxy.update_project, project.Project)

    def test_service_create_attrs(self):
        self.verify_create(self.proxy.create_service, service.Service)

    def test_service_delete(self):
        self.verify_delete(self.proxy.delete_service, service.Service, False)

    def test_service_delete_ignore(self):
        self.verify_delete(self.proxy.delete_service, service.Service, True)

    def test_service_find(self):
        self.verify_find(self.proxy.find_service, service.Service)

    def test_service_get(self):
        self.verify_get(self.proxy.get_service, service.Service)

    def test_services(self):
        self.verify_list(self.proxy.services, service.Service, paginated=False)

    def test_service_update(self):
        self.verify_update(self.proxy.update_service, service.Service)

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
        self.verify_list(self.proxy.users, user.User, paginated=False)

    def test_user_update(self):
        self.verify_update(self.proxy.update_user, user.User)

    def test_trust_create_attrs(self):
        self.verify_create(self.proxy.create_trust, trust.Trust)

    def test_trust_delete(self):
        self.verify_delete(self.proxy.delete_trust, trust.Trust, False)

    def test_trust_delete_ignore(self):
        self.verify_delete(self.proxy.delete_trust, trust.Trust, True)

    def test_trust_find(self):
        self.verify_find(self.proxy.find_trust, trust.Trust)

    def test_trust_get(self):
        self.verify_get(self.proxy.get_trust, trust.Trust)

    def test_trusts(self):
        self.verify_list(self.proxy.trusts, trust.Trust, paginated=False)

    def test_region_create_attrs(self):
        self.verify_create(self.proxy.create_region, region.Region)

    def test_region_delete(self):
        self.verify_delete(self.proxy.delete_region, region.Region, False)

    def test_region_delete_ignore(self):
        self.verify_delete(self.proxy.delete_region, region.Region, True)

    def test_region_find(self):
        self.verify_find(self.proxy.find_region, region.Region)

    def test_region_get(self):
        self.verify_get(self.proxy.get_region, region.Region)

    def test_regions(self):
        self.verify_list(self.proxy.regions, region.Region, paginated=False)

    def test_region_update(self):
        self.verify_update(self.proxy.update_region, region.Region)

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
        self.verify_list(self.proxy.roles, role.Role, paginated=False)

    def test_role_update(self):
        self.verify_update(self.proxy.update_role, role.Role)
