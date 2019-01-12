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

from openstack import resource
from openstack import utils


class Project(resource.Resource, resource.TagMixin):
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

    _query_mapping = resource.QueryParameters(
        'domain_id',
        'is_domain',
        'name',
        'parent_id',
        is_enabled='enabled',
        **resource.TagMixin._tag_query_parameters
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
    #: Unique project name, within the owning domain. *Type: string*
    name = resource.Body('name')
    #: The ID of the parent of the project.
    #: New in version 3.4
    parent_id = resource.Body('parent_id')

    def assign_role_to_user(self, session, user, role):
        """Assign role to user on project"""
        url = utils.urljoin(self.base_path, self.id, 'users',
                            user.id, 'roles', role.id)
        resp = session.put(url,)
        if resp.status_code == 204:
            return True
        return False

    def validate_user_has_role(self, session, user, role):
        """Validates that a user has a role on a project"""
        url = utils.urljoin(self.base_path, self.id, 'users',
                            user.id, 'roles', role.id)
        resp = session.head(url,)
        if resp.status_code == 204:
            return True
        return False

    def unassign_role_from_user(self, session, user, role):
        """Unassigns a role from a user on a project"""
        url = utils.urljoin(self.base_path, self.id, 'users',
                            user.id, 'roles', role.id)
        resp = session.delete(url,)
        if resp.status_code == 204:
            return True
        return False

    def assign_role_to_group(self, session, group, role):
        """Assign role to group on project"""
        url = utils.urljoin(self.base_path, self.id, 'groups',
                            group.id, 'roles', role.id)
        resp = session.put(url,)
        if resp.status_code == 204:
            return True
        return False

    def validate_group_has_role(self, session, group, role):
        """Validates that a group has a role on a project"""
        url = utils.urljoin(self.base_path, self.id, 'groups',
                            group.id, 'roles', role.id)
        resp = session.head(url,)
        if resp.status_code == 204:
            return True
        return False

    def unassign_role_from_group(self, session, group, role):
        """Unassigns a role from a group on a project"""
        url = utils.urljoin(self.base_path, self.id, 'groups',
                            group.id, 'roles', role.id)
        resp = session.delete(url,)
        if resp.status_code == 204:
            return True
        return False


class UserProject(Project):
    resource_key = 'project'
    resources_key = 'projects'
    base_path = '/users/%(user_id)s/projects'

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True
