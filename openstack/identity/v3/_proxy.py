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

import openstack.exceptions as exception
from openstack.identity.v3 import credential as _credential
from openstack.identity.v3 import domain as _domain
from openstack.identity.v3 import endpoint as _endpoint
from openstack.identity.v3 import group as _group
from openstack.identity.v3 import policy as _policy
from openstack.identity.v3 import project as _project
from openstack.identity.v3 import region as _region
from openstack.identity.v3 import role as _role
from openstack.identity.v3 import role_assignment as _role_assignment
from openstack.identity.v3 import role_domain_group_assignment \
    as _role_domain_group_assignment
from openstack.identity.v3 import role_domain_user_assignment \
    as _role_domain_user_assignment
from openstack.identity.v3 import role_project_group_assignment \
    as _role_project_group_assignment
from openstack.identity.v3 import role_project_user_assignment \
    as _role_project_user_assignment
from openstack.identity.v3 import service as _service
from openstack.identity.v3 import trust as _trust
from openstack.identity.v3 import user as _user
from openstack import proxy2 as proxy


class Proxy(proxy.BaseProxy):

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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the credential does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent credential.

        :returns: ``None``
        """
        self._delete(_credential.Credential, credential,
                     ignore_missing=ignore_missing)

    def find_credential(self, name_or_id, ignore_missing=True):
        """Find a single credential

        :param name_or_id: The name or ID of a credential.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.credential.Credential`
                  or None
        """
        return self._find(_credential.Credential, name_or_id,
                          ignore_missing=ignore_missing)

    def get_credential(self, credential):
        """Get a single credential

        :param credential: The value can be the ID of a credential or a
            :class:`~openstack.identity.v3.credential.Credential` instance.

        :returns: One :class:`~openstack.identity.v3.credential.Credential`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_credential.Credential, credential)

    def credentials(self, **query):
        """Retrieve a generator of credentials

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of credentials instances.
        :rtype: :class:`~openstack.identity.v3.credential.Credential`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_credential.Credential, paginated=False, **query)

    def update_credential(self, credential, **attrs):
        """Update a credential

        :param credential: Either the ID of a credential or a
            :class:`~openstack.identity.v3.credential.Credential` instance.
        :attrs kwargs: The attributes to update on the credential represented
                       by ``value``.

        :returns: The updated credential
        :rtype: :class:`~openstack.identity.v3.credential.Credential`
        """
        return self._update(_credential.Credential, credential, **attrs)

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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.domain.Domain` or None
        """
        return self._find(_domain.Domain, name_or_id,
                          ignore_missing=ignore_missing)

    def get_domain(self, domain):
        """Get a single domain

        :param domain: The value can be the ID of a domain or a
                       :class:`~openstack.identity.v3.domain.Domain` instance.

        :returns: One :class:`~openstack.identity.v3.domain.Domain`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_domain.Domain, domain)

    def domains(self, **query):
        """Retrieve a generator of domains

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of domain instances.
        :rtype: :class:`~openstack.identity.v3.domain.Domain`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_domain.Domain, paginated=False, **query)

    def update_domain(self, domain, **attrs):
        """Update a domain

        :param domain: Either the ID of a domain or a
                       :class:`~openstack.identity.v3.domain.Domain` instance.
        :attrs kwargs: The attributes to update on the domain represented
                       by ``value``.

        :returns: The updated domain
        :rtype: :class:`~openstack.identity.v3.domain.Domain`
        """
        return self._update(_domain.Domain, domain, **attrs)

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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the endpoint does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent endpoint.

        :returns: ``None``
        """
        self._delete(_endpoint.Endpoint, endpoint,
                     ignore_missing=ignore_missing)

    def find_endpoint(self, name_or_id, ignore_missing=True):
        """Find a single endpoint

        :param name_or_id: The name or ID of a endpoint.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.endpoint.Endpoint` or None
        """
        return self._find(_endpoint.Endpoint, name_or_id,
                          ignore_missing=ignore_missing)

    def get_endpoint(self, endpoint):
        """Get a single endpoint

        :param endpoint: The value can be the ID of an endpoint or a
                         :class:`~openstack.identity.v3.endpoint.Endpoint`
                         instance.

        :returns: One :class:`~openstack.identity.v3.endpoint.Endpoint`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_endpoint.Endpoint, endpoint)

    def endpoints(self, **query):
        """Retrieve a generator of endpoints

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of endpoint instances.
        :rtype: :class:`~openstack.identity.v3.endpoint.Endpoint`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_endpoint.Endpoint, paginated=False, **query)

    def update_endpoint(self, endpoint, **attrs):
        """Update a endpoint

        :param endpoint: Either the ID of a endpoint or a
                         :class:`~openstack.identity.v3.endpoint.Endpoint`
                         instance.
        :attrs kwargs: The attributes to update on the endpoint represented
                       by ``value``.

        :returns: The updated endpoint
        :rtype: :class:`~openstack.identity.v3.endpoint.Endpoint`
        """
        return self._update(_endpoint.Endpoint, endpoint, **attrs)

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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the group does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent group.

        :returns: ``None``
        """
        self._delete(_group.Group, group, ignore_missing=ignore_missing)

    def find_group(self, name_or_id, ignore_missing=True):
        """Find a single group

        :param name_or_id: The name or ID of a group.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.group.Group` or None
        """
        return self._find(_group.Group, name_or_id,
                          ignore_missing=ignore_missing)

    def get_group(self, group):
        """Get a single group

        :param group: The value can be the ID of a group or a
                      :class:`~openstack.identity.v3.group.Group`
                      instance.

        :returns: One :class:`~openstack.identity.v3.group.Group`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_group.Group, group)

    def groups(self, **query):
        """Retrieve a generator of groups

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of group instances.
        :rtype: :class:`~openstack.identity.v3.group.Group`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_group.Group, paginated=False, **query)

    def update_group(self, group, **attrs):
        """Update a group

        :param group: Either the ID of a group or a
                      :class:`~openstack.identity.v3.group.Group` instance.
        :attrs kwargs: The attributes to update on the group represented
                       by ``value``.

        :returns: The updated group
        :rtype: :class:`~openstack.identity.v3.group.Group`
        """
        return self._update(_group.Group, group, **attrs)

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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.policy.Policy` or None
        """
        return self._find(_policy.Policy, name_or_id,
                          ignore_missing=ignore_missing)

    def get_policy(self, policy):
        """Get a single policy

        :param policy: The value can be the ID of a policy or a
                       :class:`~openstack.identity.v3.policy.Policy` instance.

        :returns: One :class:`~openstack.identity.v3.policy.Policy`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_policy.Policy, policy)

    def policies(self, **query):
        """Retrieve a generator of policies

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of policy instances.
        :rtype: :class:`~openstack.identity.v3.policy.Policy`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_policy.Policy, paginated=False, **query)

    def update_policy(self, policy, **attrs):
        """Update a policy

        :param policy: Either the ID of a policy or a
                       :class:`~openstack.identity.v3.policy.Policy` instance.
        :attrs kwargs: The attributes to update on the policy represented
                       by ``value``.

        :returns: The updated policy
        :rtype: :class:`~openstack.identity.v3.policy.Policy`
        """
        return self._update(_policy.Policy, policy, **attrs)

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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the project does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent project.

        :returns: ``None``
        """
        self._delete(_project.Project, project, ignore_missing=ignore_missing)

    def find_project(self, name_or_id, ignore_missing=True):
        """Find a single project

        :param name_or_id: The name or ID of a project.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.project.Project` or None
        """
        return self._find(_project.Project, name_or_id,
                          ignore_missing=ignore_missing)

    def get_project(self, project):
        """Get a single project

        :param project: The value can be the ID of a project or a
            :class:`~openstack.identity.v3.project.Project` instance.

        :returns: One :class:`~openstack.identity.v3.project.Project`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_project.Project, project)

    def projects(self, **query):
        """Retrieve a generator of projects

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of project instances.
        :rtype: :class:`~openstack.identity.v3.project.Project`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_project.Project, paginated=False, **query)

    def update_project(self, project, **attrs):
        """Update a project

        :param project: Either the ID of a project or a
            :class:`~openstack.identity.v3.project.Project` instance.
        :attrs kwargs: The attributes to update on the project represented
                       by ``value``.

        :returns: The updated project
        :rtype: :class:`~openstack.identity.v3.project.Project`
        """
        return self._update(_project.Project, project, **attrs)

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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.service.Service` or None
        """
        return self._find(_service.Service, name_or_id,
                          ignore_missing=ignore_missing)

    def get_service(self, service):
        """Get a single service

        :param service: The value can be the ID of a service or a
            :class:`~openstack.identity.v3.service.Service` instance.

        :returns: One :class:`~openstack.identity.v3.service.Service`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_service.Service, service)

    def services(self, **query):
        """Retrieve a generator of services

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of service instances.
        :rtype: :class:`~openstack.identity.v3.service.Service`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_service.Service, paginated=False, **query)

    def update_service(self, service, **attrs):
        """Update a service

        :param service: Either the ID of a service or a
            :class:`~openstack.identity.v3.service.Service` instance.
        :attrs kwargs: The attributes to update on the service represented
                       by ``value``.

        :returns: The updated service
        :rtype: :class:`~openstack.identity.v3.service.Service`
        """
        return self._update(_service.Service, service, **attrs)

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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the user does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent user.

        :returns: ``None``
        """
        self._delete(_user.User, user, ignore_missing=ignore_missing)

    def find_user(self, name_or_id, ignore_missing=True):
        """Find a single user

        :param name_or_id: The name or ID of a user.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.user.User` or None
        """
        return self._find(_user.User, name_or_id,
                          ignore_missing=ignore_missing)

    def get_user(self, user):
        """Get a single user

        :param user: The value can be the ID of a user or a
                     :class:`~openstack.identity.v3.user.User` instance.

        :returns: One :class:`~openstack.identity.v3.user.User`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_user.User, user)

    def users(self, **query):
        """Retrieve a generator of users

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of user instances.
        :rtype: :class:`~openstack.identity.v3.user.User`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_user.User, paginated=False, **query)

    def update_user(self, user, **attrs):
        """Update a user

        :param user: Either the ID of a user or a
                     :class:`~openstack.identity.v3.user.User` instance.
        :attrs kwargs: The attributes to update on the user represented
                       by ``value``.

        :returns: The updated user
        :rtype: :class:`~openstack.identity.v3.user.User`
        """
        return self._update(_user.User, user, **attrs)

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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v3.trust.Trust` or None
        """
        return self._find(_trust.Trust, name_or_id,
                          ignore_missing=ignore_missing)

    def get_trust(self, trust):
        """Get a single trust

        :param trust: The value can be the ID of a trust or a
                      :class:`~openstack.identity.v3.trust.Trust` instance.

        :returns: One :class:`~openstack.identity.v3.trust.Trust`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_trust.Trust, trust)

    def trusts(self, **query):
        """Retrieve a generator of trusts

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of trust instances.
        :rtype: :class:`~openstack.identity.v3.trust.Trust`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_trust.Trust, paginated=False, **query)

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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the region does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent region.
        :returns: One :class:`~openstack.identity.v3.region.Region` or None
        """
        return self._find(_region.Region, name_or_id,
                          ignore_missing=ignore_missing)

    def get_region(self, region):
        """Get a single region

        :param region: The value can be the ID of a region or a
                       :class:`~openstack.identity.v3.region.Region` instance.

        :returns: One :class:`~openstack.identity.v3.region.Region`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no matching region can be found.
        """
        return self._get(_region.Region, region)

    def regions(self, **query):
        """Retrieve a generator of regions

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the regions being returned.

        :returns: A generator of region instances.
        :rtype: :class:`~openstack.identity.v3.region.Region`
        """
        # TODO(briancurtin): This is paginated but requires base list changes.
        return self._list(_region.Region, paginated=False, **query)

    def update_region(self, region, **attrs):
        """Update a region

        :param region: Either the ID of a region or a
                      :class:`~openstack.identity.v3.region.Region` instance.
        :attrs kwargs: The attributes to update on the region represented
                       by ``value``.

        :returns: The updated region.
        :rtype: :class:`~openstack.identity.v3.region.Region`
        """
        return self._update(_region.Region, region, **attrs)

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
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the role does not exist.
                    When set to ``True``, no exception will be thrown when
                    attempting to delete a nonexistent role.

        :returns: ``None``
        """
        self._delete(_role.Role, role, ignore_missing=ignore_missing)

    def find_role(self, name_or_id, ignore_missing=True):
        """Find a single role

        :param name_or_id: The name or ID of a role.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the role does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent role.
        :returns: One :class:`~openstack.identity.v3.role.Role` or None
        """
        return self._find(_role.Role, name_or_id,
                          ignore_missing=ignore_missing)

    def get_role(self, role):
        """Get a single role

        :param role: The value can be the ID of a role or a
                       :class:`~openstack.identity.v3.role.Role` instance.

        :returns: One :class:`~openstack.identity.v3.role.Role`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no matching role can be found.
        """
        return self._get(_role.Role, role)

    def roles(self, **query):
        """Retrieve a generator of roles

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned. The options
                                 are: domain_id, name.
        :return: A generator of role instances.
        :rtype: :class:`~openstack.identity.v3.role.Role`
        """
        return self._list(_role.Role, paginated=False, **query)

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

    def role_assignments_filter(self, domain=None, project=None, group=None,
                                user=None):
        """Retrieve a generator of roles assigned to user/group

        :param domain: Either the ID of a domain or a
                      :class:`~openstack.identity.v3.domain.Domain` instance.
        :param project: Either the ID of a project or a
                      :class:`~openstack.identity.v3.project.Project`
                      instance.
        :param group: Either the ID of a group or a
                      :class:`~openstack.identity.v3.group.Group` instance.
        :param user: Either the ID of a user or a
                     :class:`~openstack.identity.v3.user.User` instance.
        :return: A generator of role instances.
        :rtype: :class:`~openstack.identity.v3.role.Role`
        """
        if domain and project:
            raise exception.InvalidRequest(
                'Only one of domain or project can be specified')

        if domain is None and project is None:
            raise exception.InvalidRequest(
                'Either domain or project should be specified')

        if group and user:
            raise exception.InvalidRequest(
                'Only one of group or user can be specified')

        if group is None and user is None:
            raise exception.InvalidRequest(
                'Either group or user should be specified')

        if domain:
            domain = self._get_resource(_domain.Domain, domain)
            if group:
                group = self._get_resource(_group.Group, group)
                return self._list(
                    _role_domain_group_assignment.RoleDomainGroupAssignment,
                    paginated=False, domain_id=domain.id, group_id=group.id)
            else:
                user = self._get_resource(_user.User, user)
                return self._list(
                    _role_domain_user_assignment.RoleDomainUserAssignment,
                    paginated=False, domain_id=domain.id, user_id=user.id)
        else:
            project = self._get_resource(_project.Project, project)
            if group:
                group = self._get_resource(_group.Group, group)
                return self._list(
                    _role_project_group_assignment.RoleProjectGroupAssignment,
                    paginated=False, project_id=project.id, group_id=group.id)
            else:
                user = self._get_resource(_user.User, user)
                return self._list(
                    _role_project_user_assignment.RoleProjectUserAssignment,
                    paginated=False, project_id=project.id, user_id=user.id)

    def role_assignments(self, **query):
        """Retrieve a generator of role assignments

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned. The options
                                 are: group_id, role_id, scope_domain_id,
                                 scope_project_id, user_id, include_names,
                                 include_subtree.
        :return:
                :class:`~openstack.identity.v3.role_assignment.RoleAssignment`
        """
        return self._list(_role_assignment.RoleAssignment,
                          paginated=False, **query)
