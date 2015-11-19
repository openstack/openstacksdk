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

from openstack.database.v1 import database
from openstack.database.v1 import flavor
from openstack.database.v1 import instance
from openstack.database.v1 import user
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def create_database(self, **attrs):
        """Create a new database from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.database.v1.database.Database`,
                           comprised of the properties on the Database class.

        :returns: The results of server creation
        :rtype: :class:`~openstack.database.v1.database.Database`
        """
        return self._create(database.Database, **attrs)

    def delete_database(self, value, ignore_missing=True):
        """Delete a database

        :param value: The value can be either the ID of a database or a
               :class:`~openstack.database.v1.database.Database` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the database does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent database.

        :returns: ``None``
        """
        self._delete(database.Database, value, ignore_missing=ignore_missing)

    def find_database(self, name_or_id, ignore_missing=True):
        """Find a single database

        :param name_or_id: The name or ID of a database.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.database.v1.database.Database` or None
        """
        return self._find(database.Database, name_or_id,
                          ignore_missing=ignore_missing)

    def databases(self, **query):
        """Return a generator of databases

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of database objects
        :rtype: :class:`~openstack.database.v1.database.Database`
        """
        return self._list(database.Database, paginated=False, **query)

    def get_database(self, value):
        """Get a single database

        :param value: The value can be the ID of a database or a
                      :class:`~openstack.database.v1.database.Database`
                      instance.

        :returns: One :class:`~openstack.database.v1.database.Database`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(database.Database, value)

    def find_flavor(self, name_or_id, ignore_missing=True):
        """Find a single flavor

        :param name_or_id: The name or ID of a flavor.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.database.v1.flavor.Flavor` or None
        """
        return self._find(flavor.Flavor, name_or_id,
                          ignore_missing=ignore_missing)

    def get_flavor(self, value):
        """Get a single flavor

        :param value: The value can be the ID of a flavor or a
                      :class:`~openstack.database.v1.flavor.Flavor` instance.

        :returns: One :class:`~openstack.database.v1.flavor.Flavor`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(flavor.Flavor, value)

    def flavors(self, **query):
        """Return a generator of flavors

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of flavor objects
        :rtype: :class:`~openstack.database.v1.flavor.Flavor`
        """
        return self._list(flavor.Flavor, paginated=False, **query)

    def create_instance(self, **attrs):
        """Create a new instance from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.database.v1.instance.Instance`,
                           comprised of the properties on the Instance class.

        :returns: The results of server creation
        :rtype: :class:`~openstack.database.v1.instance.Instance`
        """
        return self._create(instance.Instance, **attrs)

    def delete_instance(self, value, ignore_missing=True):
        """Delete an instance

        :param value: The value can be either the ID of an instance or a
               :class:`~openstack.database.v1.instance.Instance` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the instance does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent instance.

        :returns: ``None``
        """
        self._delete(instance.Instance, value, ignore_missing=ignore_missing)

    def find_instance(self, name_or_id, ignore_missing=True):
        """Find a single instance

        :param name_or_id: The name or ID of a instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.database.v1.instance.Instance` or None
        """
        return self._find(instance.Instance, name_or_id,
                          ignore_missing=ignore_missing)

    def get_instance(self, value):
        """Get a single instance

        :param value: The value can be the ID of an instance or a
                      :class:`~openstack.database.v1.instance.Instance`
                      instance.

        :returns: One :class:`~openstack.database.v1.instance.Instance`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(instance.Instance, value)

    def instances(self, **query):
        """Return a generator of instances

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of instance objects
        :rtype: :class:`~openstack.database.v1.instance.Instance`
        """
        return self._list(instance.Instance, paginated=False, **query)

    def update_instance(self, value, **attrs):
        """Update a instance

        :param value: Either the id of a instance or a
                      :class:`~openstack.database.v1.instance.Instance`
                      instance.
        :attrs kwargs: The attributes to update on the instance represented
                       by ``value``.

        :returns: The updated instance
        :rtype: :class:`~openstack.database.v1.instance.Instance`
        """
        return self._update(instance.Instance, value, **attrs)

    def create_user(self, **attrs):
        """Create a new user from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.database.v1.user.User`,
                           comprised of the properties on the User class.

        :returns: The results of server creation
        :rtype: :class:`~openstack.database.v1.user.User`
        """
        return self._create(user.User, **attrs)

    def delete_user(self, value, ignore_missing=True):
        """Delete a user

        :param value: The value can be either the ID of a user or a
                      :class:`~openstack.database.v1.user.User` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the user does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent user.

        :returns: ``None``
        """
        self._delete(user.User, value, ignore_missing=ignore_missing)

    def find_user(self, name_or_id, ignore_missing=True):
        """Find a single user

        :param name_or_id: The name or ID of a user.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.database.v1.user.User` or None
        """
        return self._find(user.User, name_or_id, ignore_missing=ignore_missing)

    def users(self, **query):
        """Return a generator of users

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of user objects
        :rtype: :class:`~openstack.database.v1.user.User`
        """
        return self._list(user.User, paginated=False, **query)

    def get_user(self, value):
        """Get a single user

        :param value: The value can be the ID of a user or a
                      :class:`~openstack.database.v1.user.User` instance.

        :returns: One :class:`~openstack.database.v1.user.User`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(user.User, value)
