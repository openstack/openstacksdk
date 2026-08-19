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

from typing import TYPE_CHECKING

from keystoneauth1 import adapter

from openstack import resource
from openstack import utils

if TYPE_CHECKING:
    from openstack.identity.v3 import group as _group
    from openstack.identity.v3 import role as _role
    from openstack.identity.v3 import user as _user


class System(resource.Resource):
    resource_key = 'system'
    base_path = '/system'

    # capabilities

    def assign_role_to_user(
        self,
        session: adapter.Adapter,
        user: '_user.User',
        role: '_role.Role',
    ) -> bool:
        """Assign role to user on system"""
        url = utils.urljoin(self.base_path, 'users', user.id, 'roles', role.id)
        resp = session.put(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def validate_user_has_role(
        self,
        session: adapter.Adapter,
        user: '_user.User',
        role: '_role.Role',
    ) -> bool:
        """Validates that a user has a role on a system"""
        url = utils.urljoin(self.base_path, 'users', user.id, 'roles', role.id)
        resp = session.head(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def unassign_role_from_user(
        self,
        session: adapter.Adapter,
        user: '_user.User',
        role: '_role.Role',
    ) -> bool:
        """Unassigns a role from a user on a system"""
        url = utils.urljoin(self.base_path, 'users', user.id, 'roles', role.id)
        resp = session.delete(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def assign_role_to_group(
        self,
        session: adapter.Adapter,
        group: '_group.Group',
        role: '_role.Role',
    ) -> bool:
        """Assign role to group on system"""
        url = utils.urljoin(
            self.base_path, 'groups', group.id, 'roles', role.id
        )
        resp = session.put(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def validate_group_has_role(
        self,
        session: adapter.Adapter,
        group: '_group.Group',
        role: '_role.Role',
    ) -> bool:
        """Validates that a group has a role on a system"""
        url = utils.urljoin(
            self.base_path, 'groups', group.id, 'roles', role.id
        )
        resp = session.head(
            url,
        )
        if resp.status_code == 204:
            return True
        return False

    def unassign_role_from_group(
        self,
        session: adapter.Adapter,
        group: '_group.Group',
        role: '_role.Role',
    ) -> bool:
        """Unassigns a role from a group on a system"""
        url = utils.urljoin(
            self.base_path, 'groups', group.id, 'roles', role.id
        )
        resp = session.delete(
            url,
        )
        if resp.status_code == 204:
            return True
        return False
