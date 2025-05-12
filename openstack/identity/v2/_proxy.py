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

from openstack.identity.v2 import extension as _extension
from openstack.identity.v2 import role as _role
from openstack.identity.v2 import tenant as _tenant
from openstack.identity.v2 import user as _user
from openstack import proxy
from openstack import resource


class Proxy(proxy.Proxy):
    def extensions(self):
        """Retrieve a generator of extensions

        :returns: A generator of extension instances.
        :rtype: :class:`~openstack.identity.v2.extension.Extension`
        """
        return self._list(_extension.Extension)

    def get_extension(self, extension):
        """Get a single extension

        :param extension: The value can be the ID of an extension or a
            :class:`~openstack.identity.v2.extension.Extension`
            instance.

        :returns: One :class:`~openstack.identity.v2.extension.Extension`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no extension can be found.
        """
        return self._get(_extension.Extension, extension)

    def create_role(self, **attrs):
        """Create a new role from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v2.role.Role`,
            comprised of the properties on the Role class.

        :returns: The results of role creation
        :rtype: :class:`~openstack.identity.v2.role.Role`
        """
        return self._create(_role.Role, **attrs)

    def delete_role(self, role, ignore_missing=True):
        """Delete a role

        :param role: The value can be either the ID of a role or a
            :class:`~openstack.identity.v2.role.Role` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the role does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent role.

        :returns: ``None``
        """
        self._delete(_role.Role, role, ignore_missing=ignore_missing)

    def find_role(self, name_or_id, ignore_missing=True):
        """Find a single role

        :param name_or_id: The name or ID of a role.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v2.role.Role` or None
        """
        return self._find(
            _role.Role, name_or_id, ignore_missing=ignore_missing
        )

    def get_role(self, role):
        """Get a single role

        :param role: The value can be the ID of a role or a
            :class:`~openstack.identity.v2.role.Role` instance.

        :returns: One :class:`~openstack.identity.v2.role.Role`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_role.Role, role)

    def roles(self, **query):
        """Retrieve a generator of roles

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of role instances.
        :rtype: :class:`~openstack.identity.v2.role.Role`
        """
        return self._list(_role.Role, **query)

    def update_role(self, role, **attrs):
        """Update a role

        :param role: Either the ID of a role or a
            :class:`~openstack.identity.v2.role.Role` instance.
        :param attrs: The attributes to update on the role represented
            by ``role``.

        :returns: The updated role
        :rtype: :class:`~openstack.identity.v2.role.Role`
        """
        return self._update(_role.Role, role, **attrs)

    def create_tenant(self, **attrs):
        """Create a new tenant from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v2.tenant.Tenant`,
            comprised of the properties on the Tenant class.

        :returns: The results of tenant creation
        :rtype: :class:`~openstack.identity.v2.tenant.Tenant`
        """
        return self._create(_tenant.Tenant, **attrs)

    def delete_tenant(self, tenant, ignore_missing=True):
        """Delete a tenant

        :param tenant: The value can be either the ID of a tenant or a
            :class:`~openstack.identity.v2.tenant.Tenant` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the tenant does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent tenant.

        :returns: ``None``
        """
        self._delete(_tenant.Tenant, tenant, ignore_missing=ignore_missing)

    def find_tenant(self, name_or_id, ignore_missing=True):
        """Find a single tenant

        :param name_or_id: The name or ID of a tenant.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v2.tenant.Tenant` or None
        """
        return self._find(
            _tenant.Tenant, name_or_id, ignore_missing=ignore_missing
        )

    def get_tenant(self, tenant):
        """Get a single tenant

        :param tenant: The value can be the ID of a tenant or a
            :class:`~openstack.identity.v2.tenant.Tenant` instance.

        :returns: One :class:`~openstack.identity.v2.tenant.Tenant`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_tenant.Tenant, tenant)

    def tenants(self, **query):
        """Retrieve a generator of tenants

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of tenant instances.
        :rtype: :class:`~openstack.identity.v2.tenant.Tenant`
        """
        return self._list(_tenant.Tenant, **query)

    def update_tenant(self, tenant, **attrs):
        """Update a tenant

        :param tenant: Either the ID of a tenant or a
            :class:`~openstack.identity.v2.tenant.Tenant` instance.
        :param attrs: The attributes to update on the tenant represented
            by ``tenant``.

        :returns: The updated tenant
        :rtype: :class:`~openstack.identity.v2.tenant.Tenant`
        """
        return self._update(_tenant.Tenant, tenant, **attrs)

    def create_user(self, **attrs):
        """Create a new user from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.identity.v2.user.User`,
            comprised of the properties on the User class.

        :returns: The results of user creation
        :rtype: :class:`~openstack.identity.v2.user.User`
        """
        return self._create(_user.User, **attrs)

    def delete_user(self, user, ignore_missing=True):
        """Delete a user

        :param user: The value can be either the ID of a user or a
            :class:`~openstack.identity.v2.user.User` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
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
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.identity.v2.user.User` or None
        """
        return self._find(
            _user.User, name_or_id, ignore_missing=ignore_missing
        )

    def get_user(self, user):
        """Get a single user

        :param user: The value can be the ID of a user or a
            :class:`~openstack.identity.v2.user.User` instance.

        :returns: One :class:`~openstack.identity.v2.user.User`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_user.User, user)

    def users(self, **query):
        """Retrieve a generator of users

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of user instances.
        :rtype: :class:`~openstack.identity.v2.user.User`
        """
        return self._list(_user.User, **query)

    def update_user(self, user, **attrs):
        """Update a user

        :param user: Either the ID of a user or a
            :class:`~openstack.identity.v2.user.User` instance.
        :param attrs: The attributes to update on the user represented
            by ``user``.

        :returns: The updated user
        :rtype: :class:`~openstack.identity.v2.user.User`
        """
        return self._update(_user.User, user, **attrs)

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: list[str] | None = None,
        interval: int | float | None = 2,
        wait: int | None = None,
        attribute: str = 'status',
        callback: ty.Callable[[int], None] | None = None,
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
        callback: ty.Callable[[int], None] | None = None,
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
