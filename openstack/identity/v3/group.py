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

from openstack import exceptions
from openstack import resource
from openstack import utils


class Group(resource.Resource):
    resource_key = 'group'
    resources_key = 'groups'
    base_path = '/groups'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'

    _query_mapping = resource.QueryParameters(
        'domain_id',
        'name',
    )

    # Properties
    #: The description of this group. *Type: string*
    description = resource.Body('description')
    #: References the domain ID which owns the group; if a domain ID is not
    #: specified by the client, the Identity service implementation will
    #: default it to the domain ID to which the client's token is scoped.
    #: *Type: string*
    domain_id = resource.Body('domain_id')
    #: Unique group name, within the owning domain. *Type: string*
    name = resource.Body('name')

    def add_user(self, session, user):
        """Add user to the group"""
        url = utils.urljoin(self.base_path, self.id, 'users', user.id)
        resp = session.put(
            url,
        )
        exceptions.raise_from_response(resp)

    def remove_user(self, session, user):
        """Remove user from the group"""
        url = utils.urljoin(self.base_path, self.id, 'users', user.id)
        resp = session.delete(
            url,
        )
        exceptions.raise_from_response(resp)

    def check_user(self, session, user):
        """Check whether user belongs to group"""
        url = utils.urljoin(self.base_path, self.id, 'users', user.id)
        resp = session.head(
            url,
        )
        if resp.status_code == 404:
            # If we recieve 404 - treat this as False,
            # rather then returning exception
            return False
        exceptions.raise_from_response(resp)
        if resp.status_code == 204:
            return True
        return False


class UserGroup(Group):
    base_path = '/users/%(user_id)%/groups'

    #: The ID for the user from the URI of the resource
    user_id = resource.URI('user_id')

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True
