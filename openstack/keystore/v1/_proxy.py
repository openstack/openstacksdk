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

from openstack.keystore.v1 import container
from openstack.keystore.v1 import order
from openstack.keystore.v1 import secret
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def create_container(self, **data):
        return container.Container(data).create(self.session)

    def delete_container(self, value, ignore_missing=True):
        """Delete a container

        :param value: The value can be either the ID of a container or a
               :class:`~openstack.keystore.v2.container.Container` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the container does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(container.Container, value, ignore_missing)

    def find_container(self, name_or_id):
        return container.Container.find(self.session, name_or_id)

    def get_container(self, **data):
        return container.Container(data).get(self.session)

    def list_container(self):
        return container.Container.list(self.session)

    def update_container(self, **data):
        return container.Container(data).update(self.session)

    def create_order(self, **data):
        return order.Order(data).create(self.session)

    def delete_order(self, value, ignore_missing=True):
        """Delete an order

        :param value: The value can be either the ID of a order or a
                      :class:`~openstack.keystore.v2.order.Order` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the order does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(order.Order, value, ignore_missing)

    def find_order(self, name_or_id):
        return order.Order.find(self.session, name_or_id)

    def get_order(self, **data):
        return order.Order(data).get(self.session)

    def list_order(self):
        return order.Order.list(self.session)

    def update_order(self, **data):
        return order.Order(data).update(self.session)

    def create_secret(self, **data):
        return secret.Secret(data).create(self.session)

    def delete_secret(self, value, ignore_missing=True):
        """Delete a secret

        :param value: The value can be either the ID of a secret or a
                      :class:`~openstack.keystore.v2.secret.Secret` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the secret does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(secret.Secret, value, ignore_missing)

    def find_secret(self, name_or_id):
        return secret.Secret.find(self.session, name_or_id)

    def get_secret(self, **data):
        return secret.Secret(data).get(self.session)

    def list_secret(self):
        return secret.Secret.list(self.session)

    def update_secret(self, **data):
        return secret.Secret(data).update(self.session)
