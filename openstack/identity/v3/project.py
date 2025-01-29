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

from openstack.common import tag
from openstack import exceptions
from openstack import resource
from openstack import utils


class Project(resource.Resource, tag.TagMixin):
    resource_key = 'project'
    resources_key = 'projects'
    base_path = '/projects'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'

    _allow_unknown_attrs_in_body = True

    _query_mapping = resource.QueryParameters(
        'domain_id',
        'is_domain',
        'name',
        'parent_id',
        is_enabled='enabled',
        **tag.TagMixin._tag_query_parameters,
    )

    # Properties
    #: The description of the project. *Type: string*
    description = resource.Body('description')
    #: References the domain ID which owns the project; if a domain ID is not
    #: specified by the client, the Identity service implementation will
    #: default it to the domain ID to which the client's token is scoped.
    #: *Type: string*
    domain_id = resource.Body('domain_id')
    #: Indicates whether the project also acts as a domain. If set to True,
    #: the project acts as both a project and a domain. Default is False.
    #: New in version 3.6
    is_domain = resource.Body('is_domain', type=bool)
    #: Setting this attribute to ``False`` prevents users from authorizing
    #: against this project. Additionally, all pre-existing tokens authorized
    #: for the project are immediately invalidated. Re-enabling a project
    #: does not re-enable pre-existing tokens. *Type: bool*
    is_enabled = resource.Body('enabled', type=bool)
    #: The resource options for the project. Available resource options are
    #: immutable.
    options = resource.Body('options', type=dict)
    #: The ID of the parent of the project.
    #: New in version 3.4
    parent_id = resource.Body('parent_id')
    #: The links related to the project resource.
    links = resource.Body('links')

    def assign_role_to_user(self, session, user, role, inherited):
        """Assign role to user on project"""
        url = utils.urljoin(
            self.base_path,
            self.id,
            'users',
            user.id,
            'roles',
            role.id,
        )
        if inherited:
            url = utils.urljoin('OS-INHERIT', url, 'inherited_to_projects')
        resp = session.put(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def validate_user_has_role(self, session, user, role, inherited):
        """Validates that a user has a role on a project"""
        url = utils.urljoin(
            self.base_path, self.id, 'users', user.id, 'roles', role.id
        )
        if inherited:
            url = utils.urljoin('OS-INHERIT', url, 'inherited_to_projects')
        resp = session.head(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def unassign_role_from_user(self, session, user, role, inherited):
        """Unassigns a role from a user on a project"""
        url = utils.urljoin(
            self.base_path, self.id, 'users', user.id, 'roles', role.id
        )
        if inherited:
            url = utils.urljoin('OS-INHERIT', url, 'inherited_to_projects')
        resp = session.delete(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def assign_role_to_group(self, session, group, role, inherited):
        """Assign role to group on project"""
        url = utils.urljoin(
            self.base_path,
            self.id,
            'groups',
            group.id,
            'roles',
            role.id,
        )
        if inherited:
            url = utils.urljoin('OS-INHERIT', url, 'inherited_to_projects')
        resp = session.put(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def validate_group_has_role(self, session, group, role, inherited):
        """Validates that a group has a role on a project"""
        url = utils.urljoin(
            self.base_path, self.id, 'groups', group.id, 'roles', role.id
        )
        if inherited:
            url = utils.urljoin('OS-INHERIT', url, 'inherited_to_projects')
        resp = session.head(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def unassign_role_from_group(self, session, group, role, inherited):
        """Unassigns a role from a group on a project"""
        url = utils.urljoin(
            self.base_path, self.id, 'groups', group.id, 'roles', role.id
        )
        if inherited:
            url = utils.urljoin('OS-INHERIT', url, 'inherited_to_projects')
        resp = session.delete(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def associate_endpoint(self, session, endpoint_id):
        """Associate endpoint with project.

        :param session: The session to use for making this request.
        :param endpoint_id: The ID of an endpoint.
        :returns: None
        """
        url = utils.urljoin(
            '/OS-EP-FILTER/projects',
            self.id,
            'endpoints',
            endpoint_id,
        )
        response = session.put(url)
        exceptions.raise_from_response(response)

    def disassociate_endpoint(self, session, endpoint_id):
        """Disassociate endpoint from project.

        :param session: The session to use for making this request.
        :param endpoint_id: The ID of an endpoint.
        :returns: None
        """
        url = utils.urljoin(
            '/OS-EP-FILTER/projects',
            self.id,
            'endpoints',
            endpoint_id,
        )
        response = session.delete(url)
        exceptions.raise_from_response(response)


class UserProject(Project):
    base_path = '/users/%(user_id)s/projects'

    #: The ID for the user from the URI of the resource
    user_id = resource.URI('user_id')

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True


class EndpointProject(Project):
    base_path = '/OS-EP-FILTER/endpoints/%(endpoint_id)s/projects'

    #: The ID for the endpoint from the URI of the resource
    endpoint_id = resource.URI('endpoint_id')

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True
