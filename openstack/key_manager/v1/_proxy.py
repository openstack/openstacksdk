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

from openstack.key_manager.v1 import container as _container
from openstack.key_manager.v1 import order as _order
from openstack.key_manager.v1 import secret as _secret
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def create_container(self, **attrs):
        """Create a new container from attributes

        :param dict attrs: Keyword arguments which will be used to create
               a :class:`~openstack.key_manager.v1.container.Container`,
               comprised of the properties on the Container class.

        :returns: The results of container creation
        :rtype: :class:`~openstack.key_manager.v1.container.Container`
        """
        return self._create(_container.Container, **attrs)

    def delete_container(self, container, ignore_missing=True):
        """Delete a container

        :param container: The value can be either the ID of a container or a
               :class:`~openstack.key_manager.v1.container.Container`
               instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the container does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent container.

        :returns: ``None``
        """
        self._delete(_container.Container, container,
                     ignore_missing=ignore_missing)

    def find_container(self, name_or_id, ignore_missing=True):
        """Find a single container

        :param name_or_id: The name or ID of a container.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.key_manager.v1.container.Container`
                  or None
        """
        return self._find(_container.Container, name_or_id,
                          ignore_missing=ignore_missing)

    def get_container(self, container):
        """Get a single container

        :param container: The value can be the ID of a container or a
                      :class:`~openstack.key_manager.v1.container.Container`
                      instance.

        :returns: One :class:`~openstack.key_manager.v1.container.Container`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_container.Container, container)

    def containers(self, **query):
        """Return a generator of containers

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of container objects
        :rtype: :class:`~openstack.key_manager.v1.container.Container`
        """
        return self._list(_container.Container, paginated=False, **query)

    def update_container(self, container, **attrs):
        """Update a container

        :param container: Either the id of a container or a
                      :class:`~openstack.key_manager.v1.container.Container`
                      instance.
        :attrs kwargs: The attributes to update on the container represented
                       by ``value``.

        :returns: The updated container
        :rtype: :class:`~openstack.key_manager.v1.container.Container`
        """
        return self._update(_container.Container, container, **attrs)

    def create_order(self, **attrs):
        """Create a new order from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.key_manager.v1.order.Order`,
                           comprised of the properties on the Order class.

        :returns: The results of order creation
        :rtype: :class:`~openstack.key_manager.v1.order.Order`
        """
        return self._create(_order.Order, **attrs)

    def delete_order(self, order, ignore_missing=True):
        """Delete an order

        :param order: The value can be either the ID of a order or a
                      :class:`~openstack.key_manager.v1.order.Order`
                      instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the order does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent order.

        :returns: ``None``
        """
        self._delete(_order.Order, order, ignore_missing=ignore_missing)

    def find_order(self, name_or_id, ignore_missing=True):
        """Find a single order

        :param name_or_id: The name or ID of a order.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.key_manager.v1.order.Order` or None
        """
        return self._find(_order.Order, name_or_id,
                          ignore_missing=ignore_missing)

    def get_order(self, order):
        """Get a single order

        :param order: The value can be the ID of an order or a
                      :class:`~openstack.key_manager.v1.order.Order`
                      instance.

        :returns: One :class:`~openstack.key_manager.v1.order.Order`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_order.Order, order)

    def orders(self, **query):
        """Return a generator of orders

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of order objects
        :rtype: :class:`~openstack.key_manager.v1.order.Order`
        """
        return self._list(_order.Order, paginated=False, **query)

    def update_order(self, order, **attrs):
        """Update a order

        :param order: Either the id of a order or a
                      :class:`~openstack.key_manager.v1.order.Order`
                      instance.
        :attrs kwargs: The attributes to update on the order represented
                       by ``value``.

        :returns: The updated order
        :rtype: :class:`~openstack.key_manager.v1.order.Order`
        """
        return self._update(_order.Order, order, **attrs)

    def create_secret(self, **attrs):
        """Create a new secret from attributes

        :param dict attrs: Keyword arguments which will be used to create a
                           :class:`~openstack.key_manager.v1.secret.Secret`,
                           comprised of the properties on the Order class.

        :returns: The results of secret creation
        :rtype: :class:`~openstack.key_manager.v1.secret.Secret`
        """
        return self._create(_secret.Secret, **attrs)

    def delete_secret(self, secret, ignore_missing=True):
        """Delete a secret

        :param secret: The value can be either the ID of a secret or a
                       :class:`~openstack.key_manager.v1.secret.Secret`
                       instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the secret does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent secret.

        :returns: ``None``
        """
        self._delete(_secret.Secret, secret, ignore_missing=ignore_missing)

    def find_secret(self, name_or_id, ignore_missing=True):
        """Find a single secret

        :param name_or_id: The name or ID of a secret.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.key_manager.v1.secret.Secret` or
                  None
        """
        return self._find(_secret.Secret, name_or_id,
                          ignore_missing=ignore_missing)

    def get_secret(self, secret):
        """Get a single secret

        :param secret: The value can be the ID of a secret or a
                       :class:`~openstack.key_manager.v1.secret.Secret`
                       instance.

        :returns: One :class:`~openstack.key_manager.v1.secret.Secret`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_secret.Secret, secret)

    def secrets(self, **query):
        """Return a generator of secrets

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of secret objects
        :rtype: :class:`~openstack.key_manager.v1.secret.Secret`
        """
        return self._list(_secret.Secret, paginated=False, **query)

    def update_secret(self, secret, **attrs):
        """Update a secret

        :param secret: Either the id of a secret or a
                       :class:`~openstack.key_manager.v1.secret.Secret`
                       instance.
        :attrs kwargs: The attributes to update on the secret represented
                       by ``value``.

        :returns: The updated secret
        :rtype: :class:`~openstack.key_manager.v1.secret.Secret`
        """
        return self._update(_secret.Secret, secret, **attrs)
