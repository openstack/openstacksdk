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

import typing as ty

import openstack.exceptions as exception
from openstack.identity.v3 import (
    application_credential as _application_credential,
)
from openstack.identity.v3 import access_rule as _access_rule
from openstack.identity.v3 import credential as _credential
from openstack.identity.v3 import domain as _domain
from openstack.identity.v3 import domain_config as _domain_config
from openstack.identity.v3 import endpoint as _endpoint
from openstack.identity.v3 import federation_protocol as _federation_protocol
from openstack.identity.v3 import group as _group
from openstack.identity.v3 import identity_provider as _identity_provider
from openstack.identity.v3 import limit as _limit
from openstack.identity.v3 import mapping as _mapping
from openstack.identity.v3 import policy as _policy
from openstack.identity.v3 import project as _project
from openstack.identity.v3 import region as _region
from openstack.identity.v3 import registered_limit as _registered_limit
from openstack.identity.v3 import role as _role
from openstack.identity.v3 import role_assignment as _role_assignment
from openstack.identity.v3 import (
    role_domain_group_assignment as _role_domain_group_assignment,
)
from openstack.identity.v3 import (
    role_domain_user_assignment as _role_domain_user_assignment,
)
from openstack.identity.v3 import (
    role_project_group_assignment as _role_project_group_assignment,
)
from openstack.identity.v3 import (
    role_project_user_assignment as _role_project_user_assignment,
)
from openstack.identity.v3 import (
    role_system_group_assignment as _role_system_group_assignment,
)
from openstack.identity.v3 import (
    role_system_user_assignment as _role_system_user_assignment,
)
from openstack.identity.v3 import service as _service
from openstack.identity.v3 import service_provider as _service_provider
from openstack.identity.v3 import system as _system
from openstack.identity.v3 import trust as _trust
from openstack.identity.v3 import user as _user
from openstack import proxy
from openstack import resource
from openstack import utils


class Proxy(proxy.Proxy):
    _resource_registry = {
        "application_credential": _application_credential.ApplicationCredential,  # noqa: E501
        "access_rule": _access_rule.AccessRule,
        "credential": _credential.Credential,
        "domain": _domain.Domain,
        "endpoint": _endpoint.Endpoint,
        "federation_protocol": _federation_protocol.FederationProtocol,
        "group": _group.Group,
        "identity_provider": _identity_provider.IdentityProvider,
        "limit": _limit.Limit,
        "mapping": _mapping.Mapping,
        "policy": _policy.Policy,
        "project": _project.Project,
        "region": _region.Region,
        "registered_limit": _registered_limit.RegisteredLimit,
        "role": _role.Role,
        "role_assignment": _role_assignment.RoleAssignment,
        "role_domain_group_assignment": _role_domain_group_assignment.RoleDomainGroupAssignment,  # noqa: E501
        "role_domain_user_assignment": _role_domain_user_assignment.RoleDomainUserAssignment,  # noqa: E501
        "role_project_group_assignment": _role_project_group_assignment.RoleProjectGroupAssignment,  # noqa: E501
        "role_project_user_assignment": _role_project_user_assignment.RoleProjectUserAssignment,  # noqa: E501
        "role_system_group_assignment": _role_system_group_assignment.RoleSystemGroupAssignment,  # noqa: E501
        "role_system_user_assignment": _role_system_user_assignment.RoleSystemUserAssignment,  # noqa: E501
        "service": _service.Service,
        "system": _system.System,
        "trust": _trust.Trust,
        "user": _user.User,
    }

    # ========== Credentials ==========

    def create_credential(self, **attrs):
        """Create a new credential from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.credential.Credential`,
            comprised of the properties on the Credential class.

        :returns: The results of credential creation
        :rtype: :class:`~openstack.identity.v3.credential.Credential`
        """
        return self._create(_credential.Credential, **attrs)

    def delete_credential(self, credential, ignore_missing=True):
        """Delete a credential

        :param credential: The value can be either the ID of a credential or a
            :class:`~openstack.identity.v3.credential.Credential` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the credential does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent credential.

        :returns: ``None``
        """
        self._delete(
            _credential.Credential, credential, ignore_missing=ignore_missing
        )

    def find_credential(self, name_or_id, ignore_missing=True):
        """Find a single credential

        :param name_or_id: The name or ID of a credential.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.credential.Credential`
            or None
        """
        return self._find(
            _credential.Credential, name_or_id, ignore_missing=ignore_missing
        )

    def get_credential(self, credential):
        """Get a single credential

        :param credential: The value can be the ID of a credential or a
            :class:`~openstack.identity.v3.credential.Credential` instance.

        :returns: One :class:`~openstack.identity.v3.credential.Credential`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_credential.Credential, credential)

    def credentials(self, **query):
        """Retrieve a generator of credentials

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of credentials instances.
        :rtype: :class:`~openstack.identity.v3.credential.Credential`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_credential.Credential, **query)

    def update_credential(self, credential, **attrs):
        """Update a credential

        :param credential: Either the ID of a credential or a
            :class:`~openstack.identity.v3.credential.Credential` instance.
        :param attrs: The attributes to update on the credential represented
            by ``credential``.

        :returns: The updated credential
        :rtype: :class:`~openstack.identity.v3.credential.Credential`
        """
        return self._update(_credential.Credential, credential, **attrs)

    # ========== Domains ==========

    def create_domain(self, **attrs):
        """Create a new domain from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.domain.Domain`,
            comprised of the properties on the Domain class.

        :returns: The results of domain creation
        :rtype: :class:`~openstack.identity.v3.domain.Domain`
        """
        return self._create(_domain.Domain, **attrs)

    def delete_domain(self, domain, ignore_missing=True):
        """Delete a domain

        :param domain: The value can be either the ID of a domain or a
            :class:`~openstack.identity.v3.domain.Domain` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the domain does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent domain.

        :returns: ``None``
        """
        self._delete(_domain.Domain, domain, ignore_missing=ignore_missing)

    def find_domain(self, name_or_id, ignore_missing=True):
        """Find a single domain

        :param name_or_id: The name or ID of a domain.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.domain.Domain` or None
        """
        return self._find(
            _domain.Domain, name_or_id, ignore_missing=ignore_missing
        )

    def get_domain(self, domain):
        """Get a single domain

        :param domain: The value can be the ID of a domain or a
            :class:`~openstack.identity.v3.domain.Domain` instance.

        :returns: One :class:`~openstack.identity.v3.domain.Domain`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_domain.Domain, domain)

    def domains(self, **query):
        """Retrieve a generator of domains

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of domain instances.
        :rtype: :class:`~openstack.identity.v3.domain.Domain`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_domain.Domain, **query)

    def update_domain(self, domain, **attrs):
        """Update a domain

        :param domain: Either the ID of a domain or a
            :class:`~openstack.identity.v3.domain.Domain` instance.
        :param attrs: The attributes to update on the domain represented
            by ``domain``.

        :returns: The updated domain
        :rtype: :class:`~openstack.identity.v3.domain.Domain`
        """
        return self._update(_domain.Domain, domain, **attrs)

    # ========== Domain configs ==========

    def create_domain_config(self, domain, **attrs):
        """Create a new config for a domain from attributes.

        :param domain: The value can be the ID of a domain or
            a :class:`~openstack.identity.v3.domain.Domain` instance.
        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.identity.v3.domain_config.DomainConfig`
            comprised of the properties on the DomainConfig class.

        :returns: The results of domain config creation
        :rtype: :class:`~openstack.identity.v3.domain_config.DomainConfig`
        """
        domain_id = resource.Resource._get_id(domain)
        return self._create(
            _domain_config.DomainConfig,
            domain_id=domain_id,
            **attrs,
        )

    def delete_domain_config(self, domain, ignore_missing=True):
        """Delete a config for a domain

        :param domain: The value can be the ID of a domain or a
            a :class:`~openstack.identity.v3.domain.Domain` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the identity provider does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent config for a domain.

        :returns: ``None``
        """
        domain_id = resource.Resource._get_id(domain)
        self._delete(
            _domain_config.DomainConfig,
            None,
            domain_id=domain_id,
            ignore_missing=ignore_missing,
        )

    def get_domain_config(self, domain):
        """Get a single config for a domain

        :param domain_id: The value can be the ID of a domain or a
            :class:`~openstack.identity.v3.domain.Domain` instance.

        :returns: One
            :class:`~openstack.identity.v3.domain_config.DomainConfig`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
             resource can be found.
        """
        domain_id = resource.Resource._get_id(domain)
        return self._get(
            _domain_config.DomainConfig,
            domain_id=domain_id,
            requires_id=False,
        )

    def update_domain_config(self, domain, **attrs):
        """Update a config for a domain

        :param domain_id: The value can be the ID of a domain or a
            :class:`~openstack.identity.v3.domain.Domain` instance.
        :param attrs: The attributes to update on the config for a domain
            represented by ``domain_id``.

        :returns: The updated config for a domain
        :rtype: :class:`~openstack.identity.v3.domain_config.DomainConfig`
        """
        domain_id = resource.Resource._get_id(domain)
        return self._update(
            _domain_config.DomainConfig,
            None,
            domain_id=domain_id,
            **attrs,
        )

    # ========== Endpoints ==========

    def create_endpoint(self, **attrs):
        """Create a new endpoint from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.endpoint.Endpoint`,
            comprised of the properties on the Endpoint class.

        :returns: The results of endpoint creation
        :rtype: :class:`~openstack.identity.v3.endpoint.Endpoint`
        """
        return self._create(_endpoint.Endpoint, **attrs)

    def delete_endpoint(self, endpoint, ignore_missing=True):
        """Delete an endpoint

        :param endpoint: The value can be either the ID of an endpoint or a
            :class:`~openstack.identity.v3.endpoint.Endpoint` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the endpoint does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent endpoint.

        :returns: ``None``
        """
        self._delete(
            _endpoint.Endpoint, endpoint, ignore_missing=ignore_missing
        )

    def find_endpoint(self, name_or_id, ignore_missing=True):
        """Find a single endpoint

        :param name_or_id: The name or ID of a endpoint.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.endpoint.Endpoint` or None
        """
        return self._find(
            _endpoint.Endpoint, name_or_id, ignore_missing=ignore_missing
        )

    # TODO(stephenfin): This conflicts with Adapter.get_endpoint
    def get_endpoint(self, endpoint):  # type: ignore[override]
        """Get a single endpoint

        :param endpoint: The value can be the ID of an endpoint or a
            :class:`~openstack.identity.v3.endpoint.Endpoint`
            instance.

        :returns: One :class:`~openstack.identity.v3.endpoint.Endpoint`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_endpoint.Endpoint, endpoint)

    def endpoints(self, **query):
        """Retrieve a generator of endpoints

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of endpoint instances.
        :rtype: :class:`~openstack.identity.v3.endpoint.Endpoint`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_endpoint.Endpoint, **query)

    def update_endpoint(self, endpoint, **attrs):
        """Update a endpoint

        :param endpoint: Either the ID of an endpoint or a
            :class:`~openstack.identity.v3.endpoint.Endpoint` instance.
        :param attrs: The attributes to update on the endpoint represented
            by ``endpoint``.

        :returns: The updated endpoint
        :rtype: :class:`~openstack.identity.v3.endpoint.Endpoint`
        """
        return self._update(_endpoint.Endpoint, endpoint, **attrs)

    # ========== Project endpoints ==========

    def project_endpoints(self, project, **query):
        """Retrieve a generator of endpoints which are associated with the
        project.

        :param project: Either the project ID or an instance of
            :class:`~openstack.identity.v3.project.Project`
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of endpoint instances.
        :rtype: :class:`~openstack.identity.v3.endpoint.ProjectEndpoint`
        """
        project_id = self._get_resource(_project.Project, project).id
        return self._list(
            _endpoint.ProjectEndpoint, project_id=project_id, **query
        )

    def associate_endpoint_with_project(self, project, endpoint):
        """Creates a direct association between project and endpoint

        :param project: Either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project` instance.
        :param endpoint: Either the ID of an endpoint or a
            :class:`~openstack.identity.v3.endpoint.Endpoint` instance.
        :returns: None
        """
        project = self._get_resource(_project.Project, project)
        endpoint = self._get_resource(_endpoint.Endpoint, endpoint)
        project.associate_endpoint(self, endpoint.id)

    def disassociate_endpoint_from_project(self, project, endpoint):
        """Removes a direct association between project and endpoint

        :param project: Either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project` instance.
        :param endpoint: Either the ID of an endpoint or a
            :class:`~openstack.identity.v3.endpoint.Endpoint` instance.
        :returns: None
        """
        project = self._get_resource(_project.Project, project)
        endpoint = self._get_resource(_endpoint.Endpoint, endpoint)
        project.disassociate_endpoint(self, endpoint.id)

    # ========== Groups ==========

    def create_group(self, **attrs):
        """Create a new group from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.group.Group`,
            comprised of the properties on the Group class.

        :returns: The results of group creation
        :rtype: :class:`~openstack.identity.v3.group.Group`
        """
        return self._create(_group.Group, **attrs)

    def delete_group(self, group, ignore_missing=True):
        """Delete a group

        :param group: The value can be either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the group does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent group.

        :returns: ``None``
        """
        self._delete(_group.Group, group, ignore_missing=ignore_missing)

    def find_group(self, name_or_id, ignore_missing=True, **query):
        """Find a single group

        :param name_or_id: The name or ID of a group.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.group.Group` or None
        """
        return self._find(
            _group.Group,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_group(self, group):
        """Get a single group

        :param group: The value can be the ID of a group or a
            :class:`~openstack.identity.v3.group.Group`
            instance.

        :returns: One :class:`~openstack.identity.v3.group.Group`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_group.Group, group)

    def groups(self, **query):
        """Retrieve a generator of groups

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of group instances.
        :rtype: :class:`~openstack.identity.v3.group.Group`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_group.Group, **query)

    def update_group(self, group, **attrs):
        """Update a group

        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param attrs: The attributes to update on the group represented
            by ``group``.

        :returns: The updated group
        :rtype: :class:`~openstack.identity.v3.group.Group`
        """
        return self._update(_group.Group, group, **attrs)

    def add_user_to_group(self, user, group):
        """Add user to group

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :return: ``None``
        """
        user = self._get_resource(_user.User, user)
        group = self._get_resource(_group.Group, group)
        group.add_user(self, user)

    def remove_user_from_group(self, user, group):
        """Remove user to group

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :return: ``None``
        """
        user = self._get_resource(_user.User, user)
        group = self._get_resource(_group.Group, group)
        group.remove_user(self, user)

    def check_user_in_group(self, user, group):
        """Check whether user belongsto group

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :return: A boolean representing current relation
        """
        user = self._get_resource(_user.User, user)
        group = self._get_resource(_group.Group, group)
        return group.check_user(self, user)

    def group_users(self, group, **attrs):
        """List users in a group

        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param attrs: Only password_expires_at can be filter for result.

        :return: List of :class:`~openstack.identity.v3.user.User`
        """
        group = self._get_resource(_group.Group, group)
        base_path = utils.urljoin(group.base_path, group.id, 'users')
        users = self._list(_user.User, base_path=base_path, **attrs)
        return users

    # ========== Policies ==========

    def create_policy(self, **attrs):
        """Create a new policy from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.policy.Policy`,
            comprised of the properties on the Policy class.

        :returns: The results of policy creation
        :rtype: :class:`~openstack.identity.v3.policy.Policy`
        """
        return self._create(_policy.Policy, **attrs)

    def delete_policy(self, policy, ignore_missing=True):
        """Delete a policy

        :param policy: The value can be either the ID of a policy or a
            :class:`~openstack.identity.v3.policy.Policy` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the policy does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent policy.

        :returns: ``None``
        """
        self._delete(_policy.Policy, policy, ignore_missing=ignore_missing)

    def find_policy(self, name_or_id, ignore_missing=True):
        """Find a single policy

        :param name_or_id: The name or ID of a policy.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.policy.Policy` or None
        """
        return self._find(
            _policy.Policy, name_or_id, ignore_missing=ignore_missing
        )

    def get_policy(self, policy):
        """Get a single policy

        :param policy: The value can be the ID of a policy or a
            :class:`~openstack.identity.v3.policy.Policy` instance.

        :returns: One :class:`~openstack.identity.v3.policy.Policy`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_policy.Policy, policy)

    def policies(self, **query):
        """Retrieve a generator of policies

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of policy instances.
        :rtype: :class:`~openstack.identity.v3.policy.Policy`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_policy.Policy, **query)

    def update_policy(self, policy, **attrs):
        """Update a policy

        :param policy: Either the ID of a policy or a
            :class:`~openstack.identity.v3.policy.Policy` instance.
        :param attrs: The attributes to update on the policy represented
            by ``policy``.

        :returns: The updated policy
        :rtype: :class:`~openstack.identity.v3.policy.Policy`
        """
        return self._update(_policy.Policy, policy, **attrs)

    # ========== Project ==========

    def create_project(self, **attrs):
        """Create a new project from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.project.Project`,
            comprised of the properties on the Project class.

        :returns: The results of project creation
        :rtype: :class:`~openstack.identity.v3.project.Project`
        """
        return self._create(_project.Project, **attrs)

    def delete_project(self, project, ignore_missing=True):
        """Delete a project

        :param project: The value can be either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the project does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent project.

        :returns: ``None``
        """
        self._delete(_project.Project, project, ignore_missing=ignore_missing)

    def find_project(self, name_or_id, ignore_missing=True, **query):
        """Find a single project

        :param name_or_id: The name or ID of a project.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.project.Project` or None
        """
        return self._find(
            _project.Project,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_project(self, project):
        """Get a single project

        :param project: The value can be the ID of a project or a
            :class:`~openstack.identity.v3.project.Project` instance.

        :returns: One :class:`~openstack.identity.v3.project.Project`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_project.Project, project)

    def projects(self, **query):
        """Retrieve a generator of projects

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of project instances.
        :rtype: :class:`~openstack.identity.v3.project.Project`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_project.Project, **query)

    def user_projects(self, user, **query):
        """Retrieve a generator of projects to which the user has authorization
           to access.

        :param user: Either the user id or an instance of
            :class:`~openstack.identity.v3.user.User`
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of project instances.
        :rtype: :class:`~openstack.identity.v3.project.UserProject`
        """
        user = self._get_resource(_user.User, user)
        return self._list(_project.UserProject, user_id=user.id, **query)

    def endpoint_projects(self, endpoint, **query):
        """Retrieve a generator of projects which are associated with the
        endpoint.

        :param endpoint: Either the endpoint ID or an instance of
            :class:`~openstack.identity.v3.endpoint.Endpoint`
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of project instances.
        :rtype: :class:`~openstack.identity.v3.project.EndpointProject`
        """
        endpoint_id = self._get_resource(_endpoint.Endpoint, endpoint).id
        return self._list(
            _project.EndpointProject, endpoint_id=endpoint_id, **query
        )

    def update_project(self, project, **attrs):
        """Update a project

        :param project: Either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project` instance.
        :param attrs: The attributes to update on the project represented
            by ``project``.

        :returns: The updated project
        :rtype: :class:`~openstack.identity.v3.project.Project`
        """
        return self._update(_project.Project, project, **attrs)

    # ========== Services ==========

    def create_service(self, **attrs):
        """Create a new service from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.service.Service`,
            comprised of the properties on the Service class.

        :returns: The results of service creation
        :rtype: :class:`~openstack.identity.v3.service.Service`
        """
        return self._create(_service.Service, **attrs)

    def delete_service(self, service, ignore_missing=True):
        """Delete a service

        :param service: The value can be either the ID of a service or a
            :class:`~openstack.identity.v3.service.Service` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the service does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent service.

        :returns: ``None``
        """
        self._delete(_service.Service, service, ignore_missing=ignore_missing)

    def find_service(self, name_or_id, ignore_missing=True):
        """Find a single service

        :param name_or_id: The name or ID of a service.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.service.Service` or None
        """
        return self._find(
            _service.Service, name_or_id, ignore_missing=ignore_missing
        )

    def get_service(self, service):
        """Get a single service

        :param service: The value can be the ID of a service or a
            :class:`~openstack.identity.v3.service.Service` instance.

        :returns: One :class:`~openstack.identity.v3.service.Service`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_service.Service, service)

    def services(self, **query):
        """Retrieve a generator of services

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of service instances.
        :rtype: :class:`~openstack.identity.v3.service.Service`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_service.Service, **query)

    def update_service(self, service, **attrs):
        """Update a service

        :param service: Either the ID of a service or a
            :class:`~openstack.identity.v3.service.Service` instance.
        :param attrs: The attributes to update on the service represented
            by ``service``.

        :returns: The updated service
        :rtype: :class:`~openstack.identity.v3.service.Service`
        """
        return self._update(_service.Service, service, **attrs)

    # ========== Users ==========

    def create_user(self, **attrs):
        """Create a new user from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.user.User`,
            comprised of the properties on the User class.

        :returns: The results of user creation
        :rtype: :class:`~openstack.identity.v3.user.User`
        """
        return self._create(_user.User, **attrs)

    def delete_user(self, user, ignore_missing=True):
        """Delete a user

        :param user: The value can be either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the user does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent user.

        :returns: ``None``
        """
        self._delete(_user.User, user, ignore_missing=ignore_missing)

    def find_user(self, name_or_id, ignore_missing=True, **query):
        """Find a single user

        :param name_or_id: The name or ID of a user.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.user.User` or None
        """
        return self._find(
            _user.User,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_user(self, user):
        """Get a single user

        :param user: The value can be the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.

        :returns: One :class:`~openstack.identity.v3.user.User`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_user.User, user)

    def user_groups(self, user):
        """List groups a user is in

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance

        :return: List of :class:`~openstack.identity.v3.group.group`
        """
        user_id = self._get_resource(_user.User, user).id
        groups = self._list(_group.UserGroup, user_id=user_id)
        return groups

    def users(self, **query):
        """Retrieve a generator of users

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of user instances.
        :rtype: :class:`~openstack.identity.v3.user.User`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_user.User, **query)

    def update_user(self, user, **attrs):
        """Update a user

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param attrs: The attributes to update on the user represented
            by ``attrs``.

        :returns: The updated user
        :rtype: :class:`~openstack.identity.v3.user.User`
        """
        return self._update(_user.User, user, **attrs)

    # ========== Trusts ==========

    def create_trust(self, **attrs):
        """Create a new trust from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.trust.Trust`,
            comprised of the properties on the Trust class.

        :returns: The results of trust creation
        :rtype: :class:`~openstack.identity.v3.trust.Trust`
        """
        return self._create(_trust.Trust, **attrs)

    def delete_trust(self, trust, ignore_missing=True):
        """Delete a trust

        :param trust: The value can be either the ID of a trust or a
            :class:`~openstack.identity.v3.trust.Trust` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the credential does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent credential.

        :returns: ``None``
        """
        self._delete(_trust.Trust, trust, ignore_missing=ignore_missing)

    def find_trust(self, name_or_id, ignore_missing=True):
        """Find a single trust

        :param name_or_id: The name or ID of a trust.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.trust.Trust` or None
        """
        return self._find(
            _trust.Trust, name_or_id, ignore_missing=ignore_missing
        )

    def get_trust(self, trust):
        """Get a single trust

        :param trust: The value can be the ID of a trust or a
            :class:`~openstack.identity.v3.trust.Trust` instance.

        :returns: One :class:`~openstack.identity.v3.trust.Trust`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_trust.Trust, trust)

    def trusts(self, **query):
        """Retrieve a generator of trusts

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of trust instances.
        :rtype: :class:`~openstack.identity.v3.trust.Trust`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_trust.Trust, **query)

    # ========== Regions ==========

    def create_region(self, **attrs):
        """Create a new region from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.region.Region`,
            comprised of the properties on the Region class.

        :returns: The results of region creation.
        :rtype: :class:`~openstack.identity.v3.region.Region`
        """
        return self._create(_region.Region, **attrs)

    def delete_region(self, region, ignore_missing=True):
        """Delete a region

        :param region: The value can be either the ID of a region or a
            :class:`~openstack.identity.v3.region.Region` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the region does not exist.
            When set to ``True``, no exception will be thrown when
            attempting to delete a nonexistent region.

        :returns: ``None``
        """
        self._delete(_region.Region, region, ignore_missing=ignore_missing)

    def find_region(self, name_or_id, ignore_missing=True):
        """Find a single region

        :param name_or_id: The name or ID of a region.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the region does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent region.
        :returns: One :class:`~openstack.identity.v3.region.Region` or None
        """
        return self._find(
            _region.Region, name_or_id, ignore_missing=ignore_missing
        )

    def get_region(self, region):
        """Get a single region

        :param region: The value can be the ID of a region or a
            :class:`~openstack.identity.v3.region.Region` instance.

        :returns: One :class:`~openstack.identity.v3.region.Region`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no matching region can be found.
        """
        return self._get(_region.Region, region)

    def regions(self, **query):
        """Retrieve a generator of regions

        :param kwargs query: Optional query parameters to be sent to limit
            the regions being returned.

        :returns: A generator of region instances.
        :rtype: :class:`~openstack.identity.v3.region.Region`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_region.Region, **query)

    def update_region(self, region, **attrs):
        """Update a region

        :param region: Either the ID of a region or a
            :class:`~openstack.identity.v3.region.Region` instance.
        :param attrs: The attributes to update on the region represented
            by ``region``.

        :returns: The updated region.
        :rtype: :class:`~openstack.identity.v3.region.Region`
        """
        return self._update(_region.Region, region, **attrs)

    # ========== Roles ==========

    def create_role(self, **attrs):
        """Create a new role from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.role.Role`,
            comprised of the properties on the Role class.

        :returns: The results of role creation.
        :rtype: :class:`~openstack.identity.v3.role.Role`
        """
        return self._create(_role.Role, **attrs)

    def delete_role(self, role, ignore_missing=True):
        """Delete a role

        :param role: The value can be either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the role does not exist.
            When set to ``True``, no exception will be thrown when
            attempting to delete a nonexistent role.

        :returns: ``None``
        """
        self._delete(_role.Role, role, ignore_missing=ignore_missing)

    def find_role(self, name_or_id, ignore_missing=True, **query):
        """Find a single role

        :param name_or_id: The name or ID of a role.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the role does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent role.
        :returns: One :class:`~openstack.identity.v3.role.Role` or None
        """
        return self._find(
            _role.Role,
            name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def get_role(self, role):
        """Get a single role

        :param role: The value can be the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.

        :returns: One :class:`~openstack.identity.v3.role.Role`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no matching role can be found.
        """
        return self._get(_role.Role, role)

    def roles(self, **query):
        """Retrieve a generator of roles

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. The options
            are: domain_id, name.
        :return: A generator of role instances.
        :rtype: :class:`~openstack.identity.v3.role.Role`
        """
        return self._list(_role.Role, **query)

    def update_role(self, role, **attrs):
        """Update a role

        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param dict kwargs: The attributes to update on the role represented
            by ``value``. Only name can be updated

        :returns: The updated role.
        :rtype: :class:`~openstack.identity.v3.role.Role`
        """
        return self._update(_role.Role, role, **attrs)

    # ========== Role assignments ==========

    def role_assignments_filter(
        self, domain=None, project=None, system=None, group=None, user=None
    ):
        """Retrieve a generator of roles assigned to user/group

        :param domain: Either the ID of a domain or a
            :class:`~openstack.identity.v3.domain.Domain` instance.
        :param project: Either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project`
            instance.
        :param system: Either the system name or a
            :class:`~openstack.identity.v3.system.System`
            instance.
        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :return: A generator of role instances.
        :rtype: :class:`~openstack.identity.v3.role.Role`
        """
        if domain and project and system:
            raise exception.InvalidRequest(
                'Only one of domain, project, or system can be specified'
            )

        if domain is None and project is None and system is None:
            raise exception.InvalidRequest(
                'Either domain, project, or system should be specified'
            )

        if group and user:
            raise exception.InvalidRequest(
                'Only one of group or user can be specified'
            )

        if group is None and user is None:
            raise exception.InvalidRequest(
                'Either group or user should be specified'
            )

        if domain:
            domain_id = resource.Resource._get_id(domain)
            if group:
                group_id = resource.Resource._get_id(group)
                return self._list(
                    _role_domain_group_assignment.RoleDomainGroupAssignment,
                    domain_id=domain_id,
                    group_id=group_id,
                )
            else:
                user_id = resource.Resource._get_id(user)
                return self._list(
                    _role_domain_user_assignment.RoleDomainUserAssignment,
                    domain_id=domain_id,
                    user_id=user_id,
                )
        elif project:
            project_id = resource.Resource._get_id(project)
            if group:
                group_id = resource.Resource._get_id(group)
                return self._list(
                    _role_project_group_assignment.RoleProjectGroupAssignment,
                    project_id=project_id,
                    group_id=group_id,
                )
            else:
                user_id = resource.Resource._get_id(user)
                return self._list(
                    _role_project_user_assignment.RoleProjectUserAssignment,
                    project_id=project_id,
                    user_id=user_id,
                )
        else:
            system_id = resource.Resource._get_id(system)
            if group:
                group_id = resource.Resource._get_id(group)
                return self._list(
                    _role_system_group_assignment.RoleSystemGroupAssignment,
                    system_id=system_id,
                    group_id=group_id,
                )
            else:
                user_id = resource.Resource._get_id(user)
                return self._list(
                    _role_system_user_assignment.RoleSystemUserAssignment,
                    system_id=system_id,
                    user_id=user_id,
                )

    def role_assignments(self, **query):
        """Retrieve a generator of role assignments

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned. The options
            are: group_id, role_id, scope_domain_id,
            scope_project_id, inherited_to, user_id, include_names,
            include_subtree.
        :return:
            :class:`~openstack.identity.v3.role_assignment.RoleAssignment`
        """
        return self._list(_role_assignment.RoleAssignment, **query)

    def assign_domain_role_to_user(
        self, domain, user, role, *, inherited=False
    ):
        """Assign role to user on a domain

        :param domain: Either the ID of a domain or a
            :class:`~openstack.identity.v3.domain.Domain` instance.
        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param bool inherited: Whether the role assignment is inherited.
        :return: ``None``
        """
        domain = self._get_resource(_domain.Domain, domain)
        user = self._get_resource(_user.User, user)
        role = self._get_resource(_role.Role, role)
        domain.assign_role_to_user(self, user, role, inherited)

    def unassign_domain_role_from_user(
        self, domain, user, role, *, inherited=False
    ):
        """Unassign role from user on a domain

        :param domain: Either the ID of a domain or a
            :class:`~openstack.identity.v3.domain.Domain` instance.
        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param bool inherited: Whether the role assignment is inherited.
        :return: ``None``
        """
        domain = self._get_resource(_domain.Domain, domain)
        user = self._get_resource(_user.User, user)
        role = self._get_resource(_role.Role, role)
        domain.unassign_role_from_user(self, user, role, inherited)

    def validate_user_has_domain_role(
        self, domain, user, role, *, inherited=False
    ):
        """Validates that a user has a role on a domain

        :param domain: Either the ID of a domain or a
            :class:`~openstack.identity.v3.domain.Domain` instance.
        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :returns: True if user has role in domain
        """
        domain = self._get_resource(_domain.Domain, domain)
        user = self._get_resource(_user.User, user)
        role = self._get_resource(_role.Role, role)
        return domain.validate_user_has_role(self, user, role, inherited)

    def assign_domain_role_to_group(
        self, domain, group, role, *, inherited=False
    ):
        """Assign role to group on a domain

        :param domain: Either the ID of a domain or a
            :class:`~openstack.identity.v3.domain.Domain` instance.
        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param bool inherited: Whether the role assignment is inherited.
        :return: ``None``
        """
        domain = self._get_resource(_domain.Domain, domain)
        group = self._get_resource(_group.Group, group)
        role = self._get_resource(_role.Role, role)
        domain.assign_role_to_group(self, group, role, inherited)

    def unassign_domain_role_from_group(
        self, domain, group, role, *, inherited=False
    ):
        """Unassign role from group on a domain

        :param domain: Either the ID of a domain or a
            :class:`~openstack.identity.v3.domain.Domain` instance.
        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param bool inherited: Whether the role assignment is inherited.
        :return: ``None``
        """
        domain = self._get_resource(_domain.Domain, domain)
        group = self._get_resource(_group.Group, group)
        role = self._get_resource(_role.Role, role)
        domain.unassign_role_from_group(self, group, role, inherited)

    def validate_group_has_domain_role(
        self, domain, group, role, *, inherited=False
    ):
        """Validates that a group has a role on a domain

        :param domain: Either the ID of a domain or a
            :class:`~openstack.identity.v3.domain.Domain` instance.
        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :returns: True if group has role on domain
        """
        domain = self._get_resource(_domain.Domain, domain)
        group = self._get_resource(_group.Group, group)
        role = self._get_resource(_role.Role, role)
        return domain.validate_group_has_role(self, group, role, inherited)

    def assign_project_role_to_user(
        self, project, user, role, *, inherited=False
    ):
        """Assign role to user on a project

        :param project: Either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project`
            instance.
        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param bool inherited: Whether the role assignment is inherited.
        :return: ``None``
        """
        project = self._get_resource(_project.Project, project)
        user = self._get_resource(_user.User, user)
        role = self._get_resource(_role.Role, role)
        project.assign_role_to_user(self, user, role, inherited)

    def unassign_project_role_from_user(
        self, project, user, role, *, inherited=False
    ):
        """Unassign role from user on a project

        :param project: Either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project`
            instance.
        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param bool inherited: Whether the role assignment is inherited.
        :return: ``None``
        """
        project = self._get_resource(_project.Project, project)
        user = self._get_resource(_user.User, user)
        role = self._get_resource(_role.Role, role)
        project.unassign_role_from_user(self, user, role, inherited)

    def validate_user_has_project_role(
        self, project, user, role, *, inherited=False
    ):
        """Validates that a user has a role on a project

        :param project: Either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project`
            instance.
        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :returns: True if user has role in project
        """
        project = self._get_resource(_project.Project, project)
        user = self._get_resource(_user.User, user)
        role = self._get_resource(_role.Role, role)
        return project.validate_user_has_role(self, user, role, inherited)

    def assign_project_role_to_group(
        self, project, group, role, *, inherited=False
    ):
        """Assign role to group on a project

        :param project: Either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project`
            instance.
        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param bool inherited: Whether the role assignment is inherited.
        :return: ``None``
        """
        project = self._get_resource(_project.Project, project)
        group = self._get_resource(_group.Group, group)
        role = self._get_resource(_role.Role, role)
        project.assign_role_to_group(self, group, role, inherited)

    def unassign_project_role_from_group(
        self, project, group, role, *, inherited=False
    ):
        """Unassign role from group on a project

        :param project: Either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project`
            instance.
        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param bool inherited: Whether the role assignment is inherited.
        :return: ``None``
        """
        project = self._get_resource(_project.Project, project)
        group = self._get_resource(_group.Group, group)
        role = self._get_resource(_role.Role, role)
        project.unassign_role_from_group(self, group, role, inherited)

    def validate_group_has_project_role(
        self, project, group, role, *, inherited=False
    ):
        """Validates that a group has a role on a project

        :param project: Either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project`
            instance.
        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :returns: True if group has role in project
        """
        project = self._get_resource(_project.Project, project)
        group = self._get_resource(_group.Group, group)
        role = self._get_resource(_role.Role, role)
        return project.validate_group_has_role(self, group, role, inherited)

    def assign_system_role_to_user(self, user, role, system):
        """Assign a role to user on a system

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param system: The system name
        :return: ``None``
        """
        user = self._get_resource(_user.User, user)
        role = self._get_resource(_role.Role, role)
        system = self._get_resource(_system.System, system)
        system.assign_role_to_user(self, user, role)

    def unassign_system_role_from_user(self, user, role, system):
        """Unassign a role from user on a system

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param system: The system name
        :return: ``None``
        """
        user = self._get_resource(_user.User, user)
        role = self._get_resource(_role.Role, role)
        system = self._get_resource(_system.System, system)
        system.unassign_role_from_user(self, user, role)

    def validate_user_has_system_role(self, user, role, system):
        """Validates that a user has a role on a system

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param system: The system name
        :returns: True if user has role in system
        """
        user = self._get_resource(_user.User, user)
        role = self._get_resource(_role.Role, role)
        system = self._get_resource(_system.System, system)
        return system.validate_user_has_role(self, user, role)

    def assign_system_role_to_group(self, group, role, system):
        """Assign a role to group on a system

        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param system: The system name
        :return: ``None``
        """
        group = self._get_resource(_group.Group, group)
        role = self._get_resource(_role.Role, role)
        system = self._get_resource(_system.System, system)
        system.assign_role_to_group(self, group, role)

    def unassign_system_role_from_group(self, group, role, system):
        """Unassign a role from group on a system

        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param system: The system name
        :return: ``None``
        """
        group = self._get_resource(_group.Group, group)
        role = self._get_resource(_role.Role, role)
        system = self._get_resource(_system.System, system)
        system.unassign_role_from_group(self, group, role)

    def validate_group_has_system_role(self, group, role, system):
        """Validates that a group has a role on a system

        :param group: Either the ID of a group or a
            :class:`~openstack.identity.v3.group.Group` instance.
        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v3.role.Role` instance.
        :param system: The system name
        :returns: True if group has role on system
        """
        group = self._get_resource(_group.Group, group)
        role = self._get_resource(_role.Role, role)
        system = self._get_resource(_system.System, system)
        return system.validate_group_has_role(self, group, role)

    # ========== Registered limits ==========

    def registered_limits(self, **query):
        """Retrieve a generator of registered_limits

        :param kwargs query: Optional query parameters to be sent to limit
            the registered_limits being returned.

        :returns: A generator of registered_limits instances.
        :rtype: :class:`~openstack.identity.v3.registered_limit.RegisteredLimit`
        """
        return self._list(_registered_limit.RegisteredLimit, **query)

    def get_registered_limit(self, registered_limit):
        """Get a single registered_limit

        :param registered_limit: The value can be the ID of a registered_limit
            or a
            :class:`~openstack.identity.v3.registered_limit.RegisteredLimit`
            instance.

        :returns: One :class:`~openstack.identity.v3.registered_limit.RegisteredLimit`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_registered_limit.RegisteredLimit, registered_limit)

    def create_registered_limit(self, **attrs):
        """Create a new registered_limit from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.identity.v3.registered_limit.RegisteredLimit`,
            comprised of the properties on the RegisteredLimit class.

        :returns: The results of registered_limit creation.
        :rtype: :class:`~openstack.identity.v3.registered_limit.RegisteredLimit`
        """
        return self._create(_registered_limit.RegisteredLimit, **attrs)

    def update_registered_limit(self, registered_limit, **attrs):
        """Update a registered_limit

        :param registered_limit: Either the ID of a registered_limit. or a
            :class:`~openstack.identity.v3.registered_limit.RegisteredLimit`
            instance.
        :param dict kwargs: The attributes to update on the registered_limit
            represented by ``value``.

        :returns: The updated registered_limit.
        :rtype:
            :class:`~openstack.identity.v3.registered_limit.RegisteredLimit`
        """
        return self._update(
            _registered_limit.RegisteredLimit, registered_limit, **attrs
        )

    def delete_registered_limit(self, registered_limit, ignore_missing=True):
        """Delete a registered_limit

        :param registered_limit: The value can be either the ID of a
            registered_limit or a
            :class:`~openstack.identity.v3.registered_limit.RegisteredLimit`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the registered_limit does not exist. When set to ``True``, no
            exception will be thrown when attempting to delete a nonexistent
            registered_limit.

        :returns: ``None``
        """
        self._delete(
            _registered_limit.RegisteredLimit,
            registered_limit,
            ignore_missing=ignore_missing,
        )

    # ========== Limits ==========

    def limits(self, **query):
        """Retrieve a generator of limits

        :param kwargs query: Optional query parameters to be sent to limit
            the limits being returned.

        :returns: A generator of limits instances.
        :rtype: :class:`~openstack.identity.v3.limit.Limit`
        """
        return self._list(_limit.Limit, **query)

    def get_limit(self, limit):
        """Get a single limit

        :param limit: The value can be the ID of a limit
            or a :class:`~openstack.identity.v3.limit.Limit` instance.

        :returns: One :class:`~openstack.identity.v3.limit.Limit`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        return self._get(_limit.Limit, limit)

    def create_limit(self, **attrs):
        """Create a new limit from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.limit.Limit`, comprised of the
            properties on the Limit class.

        :returns: The results of limit creation.
        :rtype: :class:`~openstack.identity.v3.limit.Limit`
        """
        return self._create(_limit.Limit, **attrs)

    def update_limit(self, limit, **attrs):
        """Update a limit

        :param limit: Either the ID of a limit. or a
            :class:`~openstack.identity.v3.limit.Limit` instance.
        :param dict kwargs: The attributes to update on the limit represented
            by ``value``.

        :returns: The updated limit.
        :rtype: :class:`~openstack.identity.v3.limit.Limit`
        """
        return self._update(_limit.Limit, limit, **attrs)

    def delete_limit(self, limit, ignore_missing=True):
        """Delete a limit

        :param limit: The value can be either the ID of a limit or a
            :class:`~openstack.identity.v3.limit.Limit` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the limit does not exist. When set to ``True``, no exception will
            be thrown when attempting to delete a nonexistent limit.

        :returns: ``None``
        """
        self._delete(_limit.Limit, limit, ignore_missing=ignore_missing)

    # ========== Application credentials ==========

    def application_credentials(self, user, **query):
        """Retrieve a generator of application credentials

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.

        :param kwargs query: Optional query parameters to be sent to
            limit the resources being returned.

        :returns: A generator of application credentials instances.
        :rtype:
            :class:`~openstack.identity.v3.application_credential.ApplicationCredential`
        """
        user = self._get_resource(_user.User, user)
        return self._list(
            _application_credential.ApplicationCredential,
            user_id=user.id,
            **query,
        )

    def get_application_credential(self, user, application_credential):
        """Get a single application credential

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.

        :param application_credential: The value can be the ID of a
            application credential or a
            :class:`~openstack.identity.v3.application_credential.ApplicationCredential`
            instance.

        :returns: One
            :class:`~openstack.identity.v3.application_credential.ApplicationCredential`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        user = self._get_resource(_user.User, user)
        return self._get(
            _application_credential.ApplicationCredential,
            application_credential,
            user_id=user.id,
        )

    def create_application_credential(self, user, name, **attrs):
        """Create a new application credential from attributes

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param name: The name of the application credential which is
            unique to the user.
        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.identity.v3.application_credential.ApplicationCredential`,
            comprised of the properties on the ApplicationCredential class.


        :returns: The results of application credential creation.
        :rtype:
            :class:`~openstack.identity.v3.application_credential.ApplicationCredential`
        """

        user = self._get_resource(_user.User, user)
        return self._create(
            _application_credential.ApplicationCredential,
            name=name,
            user_id=user.id,
            **attrs,
        )

    def find_application_credential(
        self,
        user,
        name_or_id,
        ignore_missing=True,
        **query,
    ):
        """Find a single application credential

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param name_or_id: The name or ID of an application credential.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.

        :returns: One
            :class:`~openstack.identity.v3.application_credential.ApplicationCredential`
            or None
        """
        user = self._get_resource(_user.User, user)
        return self._find(
            _application_credential.ApplicationCredential,
            user_id=user.id,
            name_or_id=name_or_id,
            ignore_missing=ignore_missing,
            **query,
        )

    def delete_application_credential(
        self, user, application_credential, ignore_missing=True
    ):
        """Delete an application credential

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param application credential: The value can be either the ID of an
            application credential or a
            :class:`~openstack.identity.v3.application_credential.ApplicationCredential`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the application credential does not exist. When set to
            ``True``, no exception will be thrown when attempting to delete
            a nonexistent application credential.

        :returns: ``None``
        """
        user = self._get_resource(_user.User, user)
        self._delete(
            _application_credential.ApplicationCredential,
            application_credential,
            user_id=user.id,
            ignore_missing=ignore_missing,
        )

    # ========== Federation protocols ==========

    def create_federation_protocol(self, idp_id, **attrs):
        """Create a new federation protocol from attributes

        :param idp_id: The ID of the identity provider or a
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
            representing the identity provider the protocol is to be
            attached to.
        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.identity.v3.federation_protocol.FederationProtocol`,
            comprised of the properties on the
            FederationProtocol class.

        :returns: The results of federation protocol creation
        :rtype:
            :class:`~openstack.identity.v3.federation_protocol.FederationProtocol`
        """

        idp_cls = _identity_provider.IdentityProvider
        if isinstance(idp_id, idp_cls):
            idp_id = idp_id.id
        return self._create(
            _federation_protocol.FederationProtocol, idp_id=idp_id, **attrs
        )

    def delete_federation_protocol(
        self, idp_id, protocol, ignore_missing=True
    ):
        """Delete a federation protocol

        :param idp_id: The ID of the identity provider or a
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
            representing the identity provider the protocol is attached to.
            Can be None if protocol is a
            :class:`~openstack.identity.v3.federation_protocol.FederationProtocol`
            instance.
        :param protocol: The ID of a federation protocol or a
            :class:`~openstack.identity.v3.federation_protocol.FederationProtocol`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the federation protocol does not exist.  When set to
            ``True``, no exception will be set when attempting to delete a
            nonexistent federation protocol.

        :returns: ``None``
        """
        cls = _federation_protocol.FederationProtocol
        if idp_id is None and isinstance(protocol, cls):
            idp_id = protocol.idp_id
        idp_cls = _identity_provider.IdentityProvider
        if isinstance(idp_id, idp_cls):
            idp_id = idp_id.id
        self._delete(
            cls, protocol, ignore_missing=ignore_missing, idp_id=idp_id
        )

    def find_federation_protocol(self, idp_id, protocol, ignore_missing=True):
        """Find a single federation protocol

        :param idp_id: The ID of the identity provider or a
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
            representing the identity provider the protocol is attached to.
        :param protocol: The name or ID of a federation protocol.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the resource does not exist.  When set to ``True``, None will
            be returned when attempting to find a nonexistent resource.
        :returns: One federation protocol or None
        :rtype:
            :class:`~openstack.identity.v3.federation_protocol.FederationProtocol`
        """
        idp_cls = _identity_provider.IdentityProvider
        if isinstance(idp_id, idp_cls):
            idp_id = idp_id.id
        return self._find(
            _federation_protocol.FederationProtocol,
            protocol,
            ignore_missing=ignore_missing,
            idp_id=idp_id,
        )

    def get_federation_protocol(self, idp_id, protocol):
        """Get a single federation protocol

        :param idp_id: The ID of the identity provider or a
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
            representing the identity provider the protocol is attached to.
            Can be None if protocol is a
            :class:`~openstack.identity.v3.federation_protocol.FederationProtocol`
        :param protocol: The value can be the ID of a federation protocol or a
            :class:`~openstack.identity.v3.federation_protocol.FederationProtocol`
            instance.

        :returns: One federation protocol
        :rtype:
            :class:`~openstack.identity.v3.federation_protocol.FederationProtocol`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        cls = _federation_protocol.FederationProtocol
        if idp_id is None and isinstance(protocol, cls):
            idp_id = protocol.idp_id
        idp_cls = _identity_provider.IdentityProvider
        if isinstance(idp_id, idp_cls):
            idp_id = idp_id.id
        return self._get(cls, protocol, idp_id=idp_id)

    def federation_protocols(self, idp_id, **query):
        """Retrieve a generator of federation protocols

        :param idp_id: The ID of the identity provider or a
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
            representing the identity provider the protocol is attached to.
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of federation protocol instances.
        :rtype:
            :class:`~openstack.identity.v3.federation_protocol.FederationProtocol`
        """
        idp_cls = _identity_provider.IdentityProvider
        if isinstance(idp_id, idp_cls):
            idp_id = idp_id.id
        return self._list(
            _federation_protocol.FederationProtocol, idp_id=idp_id, **query
        )

    def update_federation_protocol(self, idp_id, protocol, **attrs):
        """Update a federation protocol

        :param idp_id: The ID of the identity provider or a
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
            representing the identity provider the protocol is attached to.
            Can be None if protocol is a
            :class:`~openstack.identity.v3.federation_protocol.FederationProtocol`
        :param protocol: Either the ID of a federation protocol or a
            :class:`~openstack.identity.v3.federation_protocol.FederationProtocol`
            instance.
        :param attrs: The attributes to update on the federation protocol
            represented by ``protocol``.

        :returns: The updated federation protocol
        :rtype:
            :class:`~openstack.identity.v3.federation_protocol.FederationProtocol`
        """
        cls = _federation_protocol.FederationProtocol
        if (idp_id is None) and (isinstance(protocol, cls)):
            idp_id = protocol.idp_id
        idp_cls = _identity_provider.IdentityProvider
        if isinstance(idp_id, idp_cls):
            idp_id = idp_id.id
        return self._update(cls, protocol, idp_id=idp_id, **attrs)

    # ========== Mappings ==========

    def create_mapping(self, **attrs):
        """Create a new mapping from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v3.mapping.Mapping`,
            comprised of the properties on the Mapping class.

        :returns: The results of mapping creation
        :rtype: :class:`~openstack.identity.v3.mapping.Mapping`
        """
        return self._create(_mapping.Mapping, **attrs)

    def delete_mapping(self, mapping, ignore_missing=True):
        """Delete a mapping

        :param mapping: The ID of a mapping or a
            :class:`~openstack.identity.v3.mapping.Mapping`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the mapping does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent mapping.

        :returns: ``None``
        """
        self._delete(_mapping.Mapping, mapping, ignore_missing=ignore_missing)

    def find_mapping(self, name_or_id, ignore_missing=True):
        """Find a single mapping

        :param name_or_id: The name or ID of a mapping.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.mapping.Mapping` or None
        """
        return self._find(
            _mapping.Mapping, name_or_id, ignore_missing=ignore_missing
        )

    def get_mapping(self, mapping):
        """Get a single mapping

        :param mapping: The value can be the ID of a mapping or a
            :class:`~openstack.identity.v3.mapping.Mapping`
            instance.

        :returns: One :class:`~openstack.identity.v3.mapping.Mapping`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_mapping.Mapping, mapping)

    def mappings(self, **query):
        """Retrieve a generator of mappings

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of mapping instances.
        :rtype: :class:`~openstack.identity.v3.mapping.Mapping`
        """
        return self._list(_mapping.Mapping, **query)

    def update_mapping(self, mapping, **attrs):
        """Update a mapping

        :param mapping: Either the ID of a mapping or a
            :class:`~openstack.identity.v3.mapping.Mapping` instance.
        :param attrs: The attributes to update on the mapping represented
            by ``mapping``.

        :returns: The updated mapping
        :rtype: :class:`~openstack.identity.v3.mapping.Mapping`
        """
        return self._update(_mapping.Mapping, mapping, **attrs)

    # ========== Identity providers ==========

    def create_identity_provider(self, **attrs):
        """Create a new identity provider from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
            comprised of the properties on the IdentityProvider class.

        :returns: The results of identity provider creation
        :rtype:
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
        """
        return self._create(_identity_provider.IdentityProvider, **attrs)

    def delete_identity_provider(self, identity_provider, ignore_missing=True):
        """Delete an identity provider

        :param mapping: The ID of an identity provoder or a
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the identity provider does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent identity provider.

        :returns: ``None``
        """
        self._delete(
            _identity_provider.IdentityProvider,
            identity_provider,
            ignore_missing=ignore_missing,
        )

    def find_identity_provider(self, name_or_id, ignore_missing=True):
        """Find a single identity provider

        :param name_or_id: The name or ID of an identity provider
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: The details of an identity provider or None.
        :rtype:
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
        """
        return self._find(
            _identity_provider.IdentityProvider,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def get_identity_provider(self, identity_provider):
        """Get a single mapping

        :param mapping: The value can be the ID of an identity provider or a
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
            instance.

        :returns: The details of an identity provider.
        :rtype:
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(
            _identity_provider.IdentityProvider, identity_provider
        )

    def identity_providers(self, **query):
        """Retrieve a generator of identity providers

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of identity provider instances.
        :rtype:
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
        """
        return self._list(_identity_provider.IdentityProvider, **query)

    def update_identity_provider(self, identity_provider, **attrs):
        """Update a mapping

        :param mapping: Either the ID of an identity provider or a
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
            instance.
        :param attrs: The attributes to update on the identity_provider
            represented by ``identity_provider``.

        :returns: The updated identity provider.
        :rtype:
            :class:`~openstack.identity.v3.identity_provider.IdentityProvider`
        """
        return self._update(
            _identity_provider.IdentityProvider, identity_provider, **attrs
        )

    # ========== Access rules ==========

    def access_rules(self, user, **query):
        """Retrieve a generator of access rules

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param kwargs query: Optional query parameters to be sent to
            limit the resources being returned.

        :returns: A generator of access rules instances.
        :rtype: :class:`~openstack.identity.v3.access_rule.AccessRule`
        """
        user = self._get_resource(_user.User, user)
        return self._list(_access_rule.AccessRule, user_id=user.id, **query)

    def get_access_rule(self, user, access_rule):
        """Get a single access rule

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param access rule: The value can be the ID of an access rule or a
            :class:`~.access_rule.AccessRule` instance.

        :returns: One :class:`~.access_rule.AccessRule`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        user = self._get_resource(_user.User, user)
        return self._get(_access_rule.AccessRule, access_rule, user_id=user.id)

    def delete_access_rule(self, user, access_rule, ignore_missing=True):
        """Delete an access rule

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v3.user.User` instance.
        :param access rule: The value can be either the ID of an
            access rule or a :class:`~.access_rule.AccessRule` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the access rule does not exist. When set to ``True``, no exception
            will be thrown when attempting to delete a nonexistent access rule.

        :returns: ``None``
        """
        user = self._get_resource(_user.User, user)
        self._delete(
            _access_rule.AccessRule,
            access_rule,
            user_id=user.id,
            ignore_missing=ignore_missing,
        )

    # ========== Service providers ==========

    def create_service_provider(self, **attrs):
        """Create a new service provider from attributes

        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.identity.v3.service_provider.ServiceProvider`,
            comprised of the properties on the ServiceProvider class.

        :returns: The results of service provider creation
        :rtype:
            :class:`~openstack.identity.v3.service_provider.ServiceProvider`
        """
        return self._create(_service_provider.ServiceProvider, **attrs)

    def delete_service_provider(self, service_provider, ignore_missing=True):
        """Delete a service provider

        :param service_provider: The ID of a service provider or a
            :class:`~openstack.identity.v3.service_provider.ServiceProvider`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the service provider does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent service provider.

        :returns: ``None``
        """
        self._delete(
            _service_provider.ServiceProvider,
            service_provider,
            ignore_missing=ignore_missing,
        )

    def find_service_provider(self, name_or_id, ignore_missing=True):
        """Find a single service provider

        :param name_or_id: The name or ID of a service provider
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised when
            the resource does not exist. When set to ``True``, None will be
            returned when attempting to find a nonexistent resource.

        :returns: The details of an service provider or None.
        :rtype:
            :class:`~openstack.identity.v3.service_provider.ServiceProvider`
        """
        return self._find(
            _service_provider.ServiceProvider,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def get_service_provider(self, service_provider):
        """Get a single service provider

        :param service_provider: The value can be the ID of a service provider
            or a
            :class:`~openstack.identity.v3.server_provider.ServiceProvider`
            instance.

        :returns: The details of an service provider.
        :rtype:
            :class:`~openstack.identity.v3.service_provider.ServiceProvider`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_service_provider.ServiceProvider, service_provider)

    def service_providers(self, **query):
        """Retrieve a generator of service providers

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of service provider instances.
        :rtype:
            :class:`~openstack.identity.v3.service_provider.ServiceProvider`
        """
        return self._list(_service_provider.ServiceProvider, **query)

    def update_service_provider(self, service_provider, **attrs):
        """Update a service provider

        :param service_provider: Either the ID of an service provider or a
            :class:`~openstack.identity.v3.service_provider.ServiceProvider`
            instance.
        :param attrs: The attributes to update on the service provider
            represented by ``service_provider``.

        :returns: The updated service provider.
        :rtype:
            :class:`~openstack.identity.v3.service_provider.ServiceProvider`
        """
        return self._update(
            _service_provider.ServiceProvider, service_provider, **attrs
        )

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: ty.Optional[list[str]] = None,
        interval: ty.Union[int, float, None] = 2,
        wait: ty.Optional[int] = None,
        attribute: str = 'status',
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for the resource to be in a particular status.

        :param session: The session to use for making this request.
        :param resource: The resource to wait on to reach the status. The
            resource must have a status attribute specified via ``attribute``.
        :param status: Desired status of the resource.
        :param failures: Statuses that would indicate the transition
            failed such as 'ERROR'. Defaults to ['ERROR'].
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for transition.
            Set to ``None`` to wait forever.
        :param attribute: Name of the resource attribute that contains the
            status.
        :param callback: A callback function. This will be called with a single
            value, progress. This is API specific but is generally a percentage
            value from 0-100.

        :return: The updated resource.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if the
            transition to status failed to occur in ``wait`` seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            transitioned to one of the states in ``failures``.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute
        """
        return resource.wait_for_status(
            self, res, status, failures, interval, wait, attribute, callback
        )

    def wait_for_delete(
        self,
        res: resource.ResourceT,
        interval: int = 2,
        wait: int = 120,
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :param interval: Number of seconds to wait before to consecutive
            checks.
        :param wait: Maximum number of seconds to wait before the change.
        :param callback: A callback function. This will be called with a single
            value, progress, which is a percentage value from 0-100.

        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait, callback)
