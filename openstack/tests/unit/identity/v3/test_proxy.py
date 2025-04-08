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

import uuid

from openstack.identity.v3 import _proxy
from openstack.identity.v3 import access_rule
from openstack.identity.v3 import credential
from openstack.identity.v3 import domain
from openstack.identity.v3 import domain_config
from openstack.identity.v3 import endpoint
from openstack.identity.v3 import group
from openstack.identity.v3 import policy
from openstack.identity.v3 import project
from openstack.identity.v3 import region
from openstack.identity.v3 import role
from openstack.identity.v3 import role_domain_group_assignment
from openstack.identity.v3 import role_domain_user_assignment
from openstack.identity.v3 import role_project_group_assignment
from openstack.identity.v3 import role_project_user_assignment
from openstack.identity.v3 import role_system_group_assignment
from openstack.identity.v3 import role_system_user_assignment
from openstack.identity.v3 import service
from openstack.identity.v3 import service_provider
from openstack.identity.v3 import trust
from openstack.identity.v3 import user
from openstack.tests.unit import test_proxy_base

USER_ID = 'user-id-' + uuid.uuid4().hex
ENDPOINT_ID = 'endpoint-id-' + uuid.uuid4().hex
PROJECT_ID = 'project-id-' + uuid.uuid4().hex


class TestIdentityProxyBase(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestIdentityProxyCredential(TestIdentityProxyBase):
    def test_credential_create_attrs(self):
        self.verify_create(self.proxy.create_credential, credential.Credential)

    def test_credential_delete(self):
        self.verify_delete(
            self.proxy.delete_credential, credential.Credential, False
        )

    def test_credential_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_credential, credential.Credential, True
        )

    def test_credential_find(self):
        self.verify_find(self.proxy.find_credential, credential.Credential)

    def test_credential_get(self):
        self.verify_get(self.proxy.get_credential, credential.Credential)

    def test_credentials(self):
        self.verify_list(self.proxy.credentials, credential.Credential)

    def test_credential_update(self):
        self.verify_update(self.proxy.update_credential, credential.Credential)


class TestIdentityProxyDomain(TestIdentityProxyBase):
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
        self.verify_list(self.proxy.domains, domain.Domain)

    def test_domain_update(self):
        self.verify_update(self.proxy.update_domain, domain.Domain)


class TestIdentityProxyDomainConfig(TestIdentityProxyBase):
    def test_domain_config_create_attrs(self):
        self.verify_create(
            self.proxy.create_domain_config,
            domain_config.DomainConfig,
            method_args=['domain_id'],
            method_kwargs={},
            expected_args=[],
            expected_kwargs={
                'domain_id': 'domain_id',
            },
        )

    def test_domain_config_delete(self):
        self.verify_delete(
            self.proxy.delete_domain_config,
            domain_config.DomainConfig,
            ignore_missing=False,
            method_args=['domain_id'],
            method_kwargs={},
            expected_args=[None],
            expected_kwargs={
                'domain_id': 'domain_id',
            },
        )

    def test_domain_config_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_domain_config,
            domain_config.DomainConfig,
            ignore_missing=True,
            method_args=['domain_id'],
            method_kwargs={},
            expected_args=[None],
            expected_kwargs={
                'domain_id': 'domain_id',
            },
        )

    # no find_domain_config

    def test_domain_config_get(self):
        self.verify_get(
            self.proxy.get_domain_config,
            domain_config.DomainConfig,
            method_args=['domain_id'],
            method_kwargs={},
            expected_args=[],
            expected_kwargs={
                'domain_id': 'domain_id',
                'requires_id': False,
            },
        )

    # no domain_configs

    def test_domain_config_update(self):
        self.verify_update(
            self.proxy.update_domain_config,
            domain_config.DomainConfig,
            method_args=['domain_id'],
            method_kwargs={},
            expected_args=[None],
            expected_kwargs={
                'domain_id': 'domain_id',
            },
        )


class TestIdentityProxyEndpoint(TestIdentityProxyBase):
    def test_endpoint_create_attrs(self):
        self.verify_create(self.proxy.create_endpoint, endpoint.Endpoint)

    def test_endpoint_delete(self):
        self.verify_delete(
            self.proxy.delete_endpoint, endpoint.Endpoint, False
        )

    def test_endpoint_delete_ignore(self):
        self.verify_delete(self.proxy.delete_endpoint, endpoint.Endpoint, True)

    def test_endpoint_find(self):
        self.verify_find(self.proxy.find_endpoint, endpoint.Endpoint)

    def test_endpoint_get(self):
        self.verify_get(self.proxy.get_endpoint, endpoint.Endpoint)

    def test_endpoints(self):
        self.verify_list(self.proxy.endpoints, endpoint.Endpoint)

    def test_project_endpoints(self):
        self.verify_list(
            self.proxy.project_endpoints,
            endpoint.ProjectEndpoint,
            method_kwargs={'project': PROJECT_ID},
            expected_kwargs={'project_id': PROJECT_ID},
        )

    def test_endpoint_update(self):
        self.verify_update(self.proxy.update_endpoint, endpoint.Endpoint)


class TestIdentityProxyGroup(TestIdentityProxyBase):
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
        self.verify_list(self.proxy.groups, group.Group)

    def test_group_update(self):
        self.verify_update(self.proxy.update_group, group.Group)

    def test_add_user_to_group(self):
        self._verify(
            "openstack.identity.v3.group.Group.add_user",
            self.proxy.add_user_to_group,
            method_args=['uid', 'gid'],
            expected_args=[
                self.proxy,
                self.proxy._get_resource(user.User, 'uid'),
            ],
        )

    def test_remove_user_from_group(self):
        self._verify(
            "openstack.identity.v3.group.Group.remove_user",
            self.proxy.remove_user_from_group,
            method_args=['uid', 'gid'],
            expected_args=[
                self.proxy,
                self.proxy._get_resource(user.User, 'uid'),
            ],
        )

    def test_check_user_in_group(self):
        self._verify(
            "openstack.identity.v3.group.Group.check_user",
            self.proxy.check_user_in_group,
            method_args=['uid', 'gid'],
            expected_args=[
                self.proxy,
                self.proxy._get_resource(user.User, 'uid'),
            ],
        )

    def test_group_users(self):
        self.verify_list(
            self.proxy.group_users,
            user.User,
            method_kwargs={"group": 'group', "attrs": 1},
            expected_kwargs={"attrs": 1},
        )


class TestIdentityProxyPolicy(TestIdentityProxyBase):
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
        self.verify_list(self.proxy.policies, policy.Policy)

    def test_policy_update(self):
        self.verify_update(self.proxy.update_policy, policy.Policy)


class TestIdentityProxyProject(TestIdentityProxyBase):
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
        self.verify_list(self.proxy.projects, project.Project)

    def test_user_projects(self):
        self.verify_list(
            self.proxy.user_projects,
            project.UserProject,
            method_kwargs={'user': USER_ID},
            expected_kwargs={'user_id': USER_ID},
        )

    def test_endpoint_projects(self):
        self.verify_list(
            self.proxy.endpoint_projects,
            project.EndpointProject,
            method_kwargs={'endpoint': ENDPOINT_ID},
            expected_kwargs={'endpoint_id': ENDPOINT_ID},
        )

    def test_project_update(self):
        self.verify_update(self.proxy.update_project, project.Project)

    def test_project_associate_endpoint(self):
        self._verify(
            'openstack.identity.v3.project.Project.associate_endpoint',
            self.proxy.associate_endpoint_with_project,
            method_args=['project_id', 'endpoint_id'],
            expected_args=[self.proxy, 'endpoint_id'],
        )

    def test_project_disassociate_endpoint(self):
        self._verify(
            'openstack.identity.v3.project.Project.disassociate_endpoint',
            self.proxy.disassociate_endpoint_from_project,
            method_args=['project_id', 'endpoint_id'],
            expected_args=[self.proxy, 'endpoint_id'],
        )


class TestIdentityProxyService(TestIdentityProxyBase):
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
        self.verify_list(self.proxy.services, service.Service)

    def test_service_update(self):
        self.verify_update(self.proxy.update_service, service.Service)


class TestIdentityProxyUser(TestIdentityProxyBase):
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

    def test_user_groups(self):
        self.verify_list(
            self.proxy.user_groups,
            group.UserGroup,
            method_kwargs={"user": 'user'},
            expected_kwargs={"user_id": "user"},
        )


class TestIdentityProxyTrust(TestIdentityProxyBase):
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
        self.verify_list(self.proxy.trusts, trust.Trust)


class TestIdentityProxyRegion(TestIdentityProxyBase):
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
        self.verify_list(self.proxy.regions, region.Region)

    def test_region_update(self):
        self.verify_update(self.proxy.update_region, region.Region)


class TestIdentityProxyRole(TestIdentityProxyBase):
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


class TestIdentityProxyRoleAssignments(TestIdentityProxyBase):
    def test_role_assignments_filter__domain_user(self):
        self.verify_list(
            self.proxy.role_assignments_filter,
            role_domain_user_assignment.RoleDomainUserAssignment,
            method_kwargs={'domain': 'domain', 'user': 'user'},
            expected_kwargs={
                'domain_id': 'domain',
                'user_id': 'user',
            },
        )

    def test_role_assignments_filter__domain_group(self):
        self.verify_list(
            self.proxy.role_assignments_filter,
            role_domain_group_assignment.RoleDomainGroupAssignment,
            method_kwargs={'domain': 'domain', 'group': 'group'},
            expected_kwargs={
                'domain_id': 'domain',
                'group_id': 'group',
            },
        )

    def test_role_assignments_filter__project_user(self):
        self.verify_list(
            self.proxy.role_assignments_filter,
            role_project_user_assignment.RoleProjectUserAssignment,
            method_kwargs={'project': 'project', 'user': 'user'},
            expected_kwargs={
                'project_id': 'project',
                'user_id': 'user',
            },
        )

    def test_role_assignments_filter__project_group(self):
        self.verify_list(
            self.proxy.role_assignments_filter,
            role_project_group_assignment.RoleProjectGroupAssignment,
            method_kwargs={'project': 'project', 'group': 'group'},
            expected_kwargs={
                'project_id': 'project',
                'group_id': 'group',
            },
        )

    def test_role_assignments_filter__system_user(self):
        self.verify_list(
            self.proxy.role_assignments_filter,
            role_system_user_assignment.RoleSystemUserAssignment,
            method_kwargs={'system': 'system', 'user': 'user'},
            expected_kwargs={
                'system_id': 'system',
                'user_id': 'user',
            },
        )

    def test_role_assignments_filter__system_group(self):
        self.verify_list(
            self.proxy.role_assignments_filter,
            role_system_group_assignment.RoleSystemGroupAssignment,
            method_kwargs={'system': 'system', 'group': 'group'},
            expected_kwargs={
                'system_id': 'system',
                'group_id': 'group',
            },
        )

    def test_assign_domain_role_to_user(self):
        self._verify(
            "openstack.identity.v3.domain.Domain.assign_role_to_user",
            self.proxy.assign_domain_role_to_user,
            method_args=['dom_id'],
            method_kwargs={'user': 'uid', 'role': 'rid'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(user.User, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
                False,
            ],
        )

    def test_unassign_domain_role_from_user(self):
        self._verify(
            "openstack.identity.v3.domain.Domain.unassign_role_from_user",
            self.proxy.unassign_domain_role_from_user,
            method_args=['dom_id'],
            method_kwargs={'user': 'uid', 'role': 'rid'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(user.User, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
                False,
            ],
        )

    def test_validate_user_has_domain_role(self):
        self._verify(
            "openstack.identity.v3.domain.Domain.validate_user_has_role",
            self.proxy.validate_user_has_domain_role,
            method_args=['dom_id'],
            method_kwargs={'user': 'uid', 'role': 'rid'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(user.User, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
                False,
            ],
        )

    def test_assign_domain_role_to_group(self):
        self._verify(
            "openstack.identity.v3.domain.Domain.assign_role_to_group",
            self.proxy.assign_domain_role_to_group,
            method_args=['dom_id'],
            method_kwargs={'group': 'uid', 'role': 'rid'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(group.Group, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
                False,
            ],
        )

    def test_unassign_domain_role_from_group(self):
        self._verify(
            "openstack.identity.v3.domain.Domain.unassign_role_from_group",
            self.proxy.unassign_domain_role_from_group,
            method_args=['dom_id'],
            method_kwargs={'group': 'uid', 'role': 'rid'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(group.Group, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
                False,
            ],
        )

    def test_validate_group_has_domain_role(self):
        self._verify(
            "openstack.identity.v3.domain.Domain.validate_group_has_role",
            self.proxy.validate_group_has_domain_role,
            method_args=['dom_id'],
            method_kwargs={'group': 'uid', 'role': 'rid'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(group.Group, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
                False,
            ],
        )

    def test_assign_project_role_to_user(self):
        self._verify(
            "openstack.identity.v3.project.Project.assign_role_to_user",
            self.proxy.assign_project_role_to_user,
            method_args=['dom_id'],
            method_kwargs={'user': 'uid', 'role': 'rid'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(user.User, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
                False,
            ],
        )

    def test_unassign_project_role_from_user(self):
        self._verify(
            "openstack.identity.v3.project.Project.unassign_role_from_user",
            self.proxy.unassign_project_role_from_user,
            method_args=['dom_id'],
            method_kwargs={'user': 'uid', 'role': 'rid'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(user.User, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
                False,
            ],
        )

    def test_validate_user_has_project_role(self):
        self._verify(
            "openstack.identity.v3.project.Project.validate_user_has_role",
            self.proxy.validate_user_has_project_role,
            method_args=['dom_id'],
            method_kwargs={'user': 'uid', 'role': 'rid'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(user.User, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
                False,
            ],
        )

    def test_assign_project_role_to_group(self):
        self._verify(
            "openstack.identity.v3.project.Project.assign_role_to_group",
            self.proxy.assign_project_role_to_group,
            method_args=['dom_id'],
            method_kwargs={'group': 'uid', 'role': 'rid'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(group.Group, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
                False,
            ],
        )

    def test_unassign_project_role_from_group(self):
        self._verify(
            "openstack.identity.v3.project.Project.unassign_role_from_group",
            self.proxy.unassign_project_role_from_group,
            method_args=['dom_id'],
            method_kwargs={'group': 'uid', 'role': 'rid'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(group.Group, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
                False,
            ],
        )

    def test_validate_group_has_project_role(self):
        self._verify(
            "openstack.identity.v3.project.Project.validate_group_has_role",
            self.proxy.validate_group_has_project_role,
            method_args=['dom_id'],
            method_kwargs={'group': 'uid', 'role': 'rid'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(group.Group, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
                False,
            ],
        )

    def test_assign_system_role_to_user(self):
        self._verify(
            "openstack.identity.v3.system.System.assign_role_to_user",
            self.proxy.assign_system_role_to_user,
            method_kwargs={'user': 'uid', 'role': 'rid', 'system': 'all'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(user.User, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
            ],
        )

    def test_unassign_system_role_from_user(self):
        self._verify(
            "openstack.identity.v3.system.System.unassign_role_from_user",
            self.proxy.unassign_system_role_from_user,
            method_kwargs={'user': 'uid', 'role': 'rid', 'system': 'all'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(user.User, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
            ],
        )

    def test_validate_user_has_system_role(self):
        self._verify(
            "openstack.identity.v3.system.System.validate_user_has_role",
            self.proxy.validate_user_has_system_role,
            method_kwargs={'user': 'uid', 'role': 'rid', 'system': 'all'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(user.User, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
            ],
        )

    def test_assign_system_role_to_group(self):
        self._verify(
            "openstack.identity.v3.system.System.assign_role_to_group",
            self.proxy.assign_system_role_to_group,
            method_kwargs={'group': 'uid', 'role': 'rid', 'system': 'all'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(group.Group, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
            ],
        )

    def test_unassign_system_role_from_group(self):
        self._verify(
            "openstack.identity.v3.system.System.unassign_role_from_group",
            self.proxy.unassign_system_role_from_group,
            method_kwargs={'group': 'uid', 'role': 'rid', 'system': 'all'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(group.Group, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
            ],
        )

    def test_validate_group_has_system_role(self):
        self._verify(
            "openstack.identity.v3.system.System.validate_group_has_role",
            self.proxy.validate_group_has_system_role,
            method_kwargs={'group': 'uid', 'role': 'rid', 'system': 'all'},
            expected_args=[
                self.proxy,
                self.proxy._get_resource(group.Group, 'uid'),
                self.proxy._get_resource(role.Role, 'rid'),
            ],
        )


class TestAccessRule(TestIdentityProxyBase):
    def test_access_rule_delete(self):
        self.verify_delete(
            self.proxy.delete_access_rule,
            access_rule.AccessRule,
            False,
            method_args=[],
            method_kwargs={'user': USER_ID, 'access_rule': 'access_rule'},
            expected_args=['access_rule'],
            expected_kwargs={'user_id': USER_ID},
        )

    def test_access_rule_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_access_rule,
            access_rule.AccessRule,
            True,
            method_args=[],
            method_kwargs={'user': USER_ID, 'access_rule': 'access_rule'},
            expected_args=['access_rule'],
            expected_kwargs={'user_id': USER_ID},
        )

    def test_access_rule_get(self):
        self.verify_get(
            self.proxy.get_access_rule,
            access_rule.AccessRule,
            method_args=[],
            method_kwargs={'user': USER_ID, 'access_rule': 'access_rule'},
            expected_args=['access_rule'],
            expected_kwargs={'user_id': USER_ID},
        )

    def test_access_rules(self):
        self.verify_list(
            self.proxy.access_rules,
            access_rule.AccessRule,
            method_kwargs={'user': USER_ID},
            expected_kwargs={'user_id': USER_ID},
        )


class TestServiceProvider(TestIdentityProxyBase):
    def test_service_provider_create(self):
        self.verify_create(
            self.proxy.create_service_provider,
            service_provider.ServiceProvider,
        )

    def test_service_provider_delete(self):
        self.verify_delete(
            self.proxy.delete_service_provider,
            service_provider.ServiceProvider,
            False,
        )

    def test_service_provider_delete_ignore(self):
        self.verify_delete(
            self.proxy.delete_service_provider,
            service_provider.ServiceProvider,
            True,
        )

    def test_service_provider_find(self):
        self.verify_find(
            self.proxy.find_service_provider, service_provider.ServiceProvider
        )

    def test_service_provider_get(self):
        self.verify_get(
            self.proxy.get_service_provider,
            service_provider.ServiceProvider,
        )

    def test_service_providers(self):
        self.verify_list(
            self.proxy.service_providers,
            service_provider.ServiceProvider,
        )

    def test_service_provider_update(self):
        self.verify_update(
            self.proxy.update_service_provider,
            service_provider.ServiceProvider,
        )
