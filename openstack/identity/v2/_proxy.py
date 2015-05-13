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

from openstack.identity.v2 import role
from openstack.identity.v2 import tenant
from openstack.identity.v2 import user
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def create_role(self, **attrs):
        """Create a new role from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.compute.v2.role.Role`,
                           comprised of the properties on the Role class.

        :returns: The results of role creation
        :rtype: :class:`~openstack.compute.v2.role.Role`
        """
        return self._create(role.Role, **attrs)

    def delete_role(self, value, ignore_missing=True):
        """Delete a role

        :param value: The value can be either the ID of a role or a
                      :class:`~openstack.identity.v2.role.Role` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the role does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent role.

        :returns: ``None``
        """
        self._delete(role.Role, value, ignore_missing)

    def find_role(self, name_or_id):
        return role.Role.find(self.session, name_or_id)

    def get_role(self, value):
        """Get a single role

        :param value: The value can be the ID of a role or a
                      :class:`~openstack.identity.v2.role.Role` instance.

        :returns: One :class:`~openstack.identity.v2.role.Role`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found for this name or id.
        """
        return self._get(role.Role, value)

    def list_roles(self):
        return role.Role.list(self.session)

    def update_role(self, value, **attrs):
        """Update a role

        :param value: Either the id of a role or a
                      :class:`~openstack.compute.v2.role.Role` instance.
        :attrs kwargs: The attributes to update on the role represented
                       by ``value``.

        :returns: The updated role
        :rtype: :class:`~openstack.compute.v2.role.Role`
        """
        return self._update(role.Role, value, **attrs)

    def create_tenant(self, **attrs):
        """Create a new tenant from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.compute.v2.tenant.Tenant`,
                           comprised of the properties on the Tenant class.

        :returns: The results of tenant creation
        :rtype: :class:`~openstack.compute.v2.tenant.Tenant`
        """
        return self._create(tenant.Tenant, **attrs)

    def delete_tenant(self, value, ignore_missing=True):
        """Delete a tenant

        :param value: The value can be either the ID of a tenant or a
                      :class:`~openstack.identity.v2.tenant.Tenant` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the tenant does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent tenant.

        :returns: ``None``
        """
        self._delete(tenant.Tenant, value, ignore_missing)

    def find_tenant(self, name_or_id):
        return tenant.Tenant.find(self.session, name_or_id)

    def get_tenant(self, value):
        """Get a single tenant

        :param value: The value can be the ID of a tenant or a
                      :class:`~openstack.identity.v2.tenant.Tenant` instance.

        :returns: One :class:`~openstack.identity.v2.tenant.Tenant`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found for this name or id.
        """
        return self._get(tenant.Tenant, value)

    def list_tenants(self):
        return tenant.Tenant.list(self.session)

    def update_tenant(self, value, **attrs):
        """Update a tenant

        :param value: Either the id of a tenant or a
                      :class:`~openstack.compute.v2.tenant.Tenant` instance.
        :attrs kwargs: The attributes to update on the tenant represented
                       by ``value``.

        :returns: The updated tenant
        :rtype: :class:`~openstack.compute.v2.tenant.Tenant`
        """
        return self._update(tenant.Tenant, value, **attrs)

    def create_user(self, **attrs):
        """Create a new user from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.compute.v2.user.User`,
                           comprised of the properties on the User class.

        :returns: The results of user creation
        :rtype: :class:`~openstack.compute.v2.user.User`
        """
        return self._create(user.User, **attrs)

    def delete_user(self, value, ignore_missing=True):
        """Delete a user

        :param value: The value can be either the ID of a user or a
                      :class:`~openstack.identity.v2.user.User` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the user does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent user.

        :returns: ``None``
        """
        self._delete(user.User, value, ignore_missing)

    def find_user(self, name_or_id):
        return user.User.find(self.session, name_or_id)

    def get_user(self, value):
        """Get a single user

        :param value: The value can be the ID of a user or a
                      :class:`~openstack.identity.v2.user.User` instance.

        :returns: One :class:`~openstack.identity.v2.user.User`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found for this name or id.
        """
        return self._get(user.User, value)

    def list_users(self):
        return user.User.list(self.session)

    def update_user(self, value, **attrs):
        """Update a user

        :param value: Either the id of a user or a
                      :class:`~openstack.compute.v2.user.User` instance.
        :attrs kwargs: The attributes to update on the user represented
                       by ``value``.

        :returns: The updated user
        :rtype: :class:`~openstack.compute.v2.user.User`
        """
        return self._update(user.User, value, **attrs)
