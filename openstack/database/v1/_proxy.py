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

from openstack.database.v1 import database as _database
from openstack.database.v1 import flavor as _flavor
from openstack.database.v1 import instance as _instance
from openstack.database.v1 import user as _user
from openstack import proxy
from openstack import resource


class Proxy(proxy.Proxy):
    _resource_registry = {
        "database": _database.Database,
        "flavor": _flavor.Flavor,
        "instance": _instance.Instance,
        "user": _user.User,
    }

    def create_database(self, instance, **attrs):
        """Create a new database from attributes

        :param instance: This can be either the ID of an instance
            or a :class:`~openstack.database.v1.instance.Instance`
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.database.v1.database.Database`,
            comprised of the properties on the Database class.

        :returns: The results of server creation
        :rtype: :class:`~openstack.database.v1.database.Database`
        """
        instance = self._get_resource(_instance.Instance, instance)
        return self._create(
            _database.Database, instance_id=instance.id, **attrs
        )

    def delete_database(self, database, instance=None, ignore_missing=True):
        """Delete a database

        :param database: The value can be either the ID of a database or a
            :class:`~openstack.database.v1.database.Database` instance.
        :param instance: This parameter needs to be specified when
            an ID is given as `database`.
            It can be either the ID of an instance
            or a :class:`~openstack.database.v1.instance.Instance`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the database does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent database.

        :returns: ``None``
        """
        instance_id = self._get_uri_attribute(
            database, instance, "instance_id"
        )
        self._delete(
            _database.Database,
            database,
            instance_id=instance_id,
            ignore_missing=ignore_missing,
        )

    def find_database(self, name_or_id, instance, ignore_missing=True):
        """Find a single database

        :param name_or_id: The name or ID of a database.
        :param instance: This can be either the ID of an instance
            or a :class:`~openstack.database.v1.instance.Instance`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.database.v1.database.Database` or None
        """
        instance = self._get_resource(_instance.Instance, instance)
        return self._find(
            _database.Database,
            name_or_id,
            instance_id=instance.id,
            ignore_missing=ignore_missing,
        )

    def databases(self, instance, **query):
        """Return a generator of databases

        :param instance: This can be either the ID of an instance
            or a :class:`~openstack.database.v1.instance.Instance`
            instance that the interface belongs to.
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of database objects
        :rtype: :class:`~openstack.database.v1.database.Database`
        """
        instance = self._get_resource(_instance.Instance, instance)
        return self._list(_database.Database, instance_id=instance.id, **query)

    def get_database(self, database, instance=None):
        """Get a single database

        :param instance: This parameter needs to be specified when
            an ID is given as `database`.
            It can be either the ID of an instance
            or a :class:`~openstack.database.v1.instance.Instance`
        :param database: The value can be the ID of a database or a
            :class:`~openstack.database.v1.database.Database`
            instance.

        :returns: One :class:`~openstack.database.v1.database.Database`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_database.Database, database)

    def find_flavor(self, name_or_id, ignore_missing=True):
        """Find a single flavor

        :param name_or_id: The name or ID of a flavor.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.database.v1.flavor.Flavor` or None
        """
        return self._find(
            _flavor.Flavor, name_or_id, ignore_missing=ignore_missing
        )

    def get_flavor(self, flavor):
        """Get a single flavor

        :param flavor: The value can be the ID of a flavor or a
            :class:`~openstack.database.v1.flavor.Flavor` instance.

        :returns: One :class:`~openstack.database.v1.flavor.Flavor`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_flavor.Flavor, flavor)

    def flavors(self, **query):
        """Return a generator of flavors

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of flavor objects
        :rtype: :class:`~openstack.database.v1.flavor.Flavor`
        """
        return self._list(_flavor.Flavor, **query)

    def create_instance(self, **attrs):
        """Create a new instance from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.database.v1.instance.Instance`,
            comprised of the properties on the Instance class.

        :returns: The results of server creation
        :rtype: :class:`~openstack.database.v1.instance.Instance`
        """
        return self._create(_instance.Instance, **attrs)

    def delete_instance(self, instance, ignore_missing=True):
        """Delete an instance

        :param instance: The value can be either the ID of an instance or a
            :class:`~openstack.database.v1.instance.Instance` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the instance does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent instance.

        :returns: ``None``
        """
        self._delete(
            _instance.Instance, instance, ignore_missing=ignore_missing
        )

    def find_instance(self, name_or_id, ignore_missing=True):
        """Find a single instance

        :param name_or_id: The name or ID of a instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.database.v1.instance.Instance` or None
        """
        return self._find(
            _instance.Instance, name_or_id, ignore_missing=ignore_missing
        )

    def get_instance(self, instance):
        """Get a single instance

        :param instance: The value can be the ID of an instance or a
            :class:`~openstack.database.v1.instance.Instance`
            instance.

        :returns: One :class:`~openstack.database.v1.instance.Instance`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_instance.Instance, instance)

    def instances(self, **query):
        """Return a generator of instances

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of instance objects
        :rtype: :class:`~openstack.database.v1.instance.Instance`
        """
        return self._list(_instance.Instance, **query)

    def update_instance(self, instance, **attrs):
        """Update a instance

        :param instance: Either the id of a instance or a
            :class:`~openstack.database.v1.instance.Instance` instance.
        :param attrs: The attributes to update on the instance represented
            by ``instance``.

        :returns: The updated instance
        :rtype: :class:`~openstack.database.v1.instance.Instance`
        """
        return self._update(_instance.Instance, instance, **attrs)

    def create_user(self, instance, **attrs):
        """Create a new user from attributes

        :param instance: This can be either the ID of an instance
            or a :class:`~openstack.database.v1.instance.Instance`
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.database.v1.user.User`,
            comprised of the properties on the User class.

        :returns: The results of server creation
        :rtype: :class:`~openstack.database.v1.user.User`
        """
        instance = self._get_resource(_instance.Instance, instance)
        return self._create(_user.User, instance_id=instance.id, **attrs)

    def delete_user(self, user, instance=None, ignore_missing=True):
        """Delete a user

        :param user: The value can be either the ID of a user or a
            :class:`~openstack.database.v1.user.User` instance.
        :param instance: This parameter needs to be specified when
            an ID is given as `user`.
            It can be either the ID of an instance
            or a :class:`~openstack.database.v1.instance.Instance`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the user does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent user.

        :returns: ``None``
        """
        instance = self._get_resource(_instance.Instance, instance)
        self._delete(
            _user.User,
            user,
            ignore_missing=ignore_missing,
            instance_id=instance.id,
        )

    def find_user(self, name_or_id, instance, ignore_missing=True):
        """Find a single user

        :param name_or_id: The name or ID of a user.
        :param instance: This can be either the ID of an instance
            or a :class:`~openstack.database.v1.instance.Instance`
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.database.v1.user.User` or None
        """
        instance = self._get_resource(_instance.Instance, instance)
        return self._find(
            _user.User,
            name_or_id,
            instance_id=instance.id,
            ignore_missing=ignore_missing,
        )

    def users(self, instance, **query):
        """Return a generator of users

        :param instance: This can be either the ID of an instance
            or a :class:`~openstack.database.v1.instance.Instance`
        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of user objects
        :rtype: :class:`~openstack.database.v1.user.User`
        """
        instance = self._get_resource(_instance.Instance, instance)
        return self._list(_user.User, instance_id=instance.id, **query)

    def get_user(self, user, instance=None):
        """Get a single user

        :param user: The value can be the ID of a user or a
            :class:`~openstack.database.v1.user.User` instance.
        :param instance: This parameter needs to be specified when
            an ID is given as `database`.
            It can be either the ID of an instance
            or a :class:`~openstack.database.v1.instance.Instance`

        :returns: One :class:`~openstack.database.v1.user.User`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        instance = self._get_resource(_instance.Instance, instance)
        return self._get(_user.User, user)

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
