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

    def create_database(self, **data):
        return database.Database(data).create(self.session)

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
        self._delete(database.Database, value, ignore_missing)

    def find_database(self, name_or_id):
        return database.Database.find(self.session, name_or_id)

    def list_database(self):
        return database.Database.list(self.session)

    def find_flavor(self, name_or_id):
        return flavor.Flavor.find(self.session, name_or_id)

    def get_flavor(self, **data):
        return flavor.Flavor(data).get(self.session)

    def list_flavor(self):
        return flavor.Flavor.list(self.session)

    def create_instance(self, **data):
        return instance.Instance(data).create(self.session)

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
        self._delete(instance.Instance, value, ignore_missing)

    def find_instance(self, name_or_id):
        return instance.Instance.find(self.session, name_or_id)

    def get_instance(self, **data):
        return instance.Instance(data).get(self.session)

    def list_instance(self):
        return instance.Instance.list(self.session)

    def update_instance(self, value, **attrs):
        """Update a instance

        :param value: Either the id of a instance or a
                      :class:`~openstack.compute.v2.instance.Instance`
                      instance.
        :attrs kwargs: The attributes to update on the instance represented
                       by ``value``.

        :returns: The updated instance
        :rtype: :class:`~openstack.compute.v2.instance.Instance`
        """
        return self._update(instance.Instance, value, **attrs)

    def create_user(self, **data):
        return user.User(data).create(self.session)

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
        self._delete(user.User, value, ignore_missing)

    def find_user(self, name_or_id):
        return user.User.find(self.session, name_or_id)

    def list_user(self):
        return user.User.list(self.session)
