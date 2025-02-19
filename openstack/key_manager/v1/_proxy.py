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

from openstack.key_manager.v1 import container as _container
from openstack.key_manager.v1 import order as _order
from openstack.key_manager.v1 import secret as _secret
from openstack import proxy
from openstack import resource


class Proxy(proxy.Proxy):
    _resource_registry = {
        "container": _container.Container,
        "order": _order.Order,
        "secret": _secret.Secret,
    }

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
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the container does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent container.

        :returns: ``None``
        """
        self._delete(
            _container.Container, container, ignore_missing=ignore_missing
        )

    def find_container(self, name_or_id, ignore_missing=True):
        """Find a single container

        :param name_or_id: The name or ID of a container.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.key_manager.v1.container.Container`
            or None
        """
        return self._find(
            _container.Container, name_or_id, ignore_missing=ignore_missing
        )

    def get_container(self, container):
        """Get a single container

        :param container: The value can be the ID of a container or a
            :class:`~openstack.key_manager.v1.container.Container`
            instance.

        :returns: One :class:`~openstack.key_manager.v1.container.Container`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_container.Container, container)

    def containers(self, **query):
        """Return a generator of containers

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of container objects
        :rtype: :class:`~openstack.key_manager.v1.container.Container`
        """
        return self._list(_container.Container, **query)

    def update_container(self, container, **attrs):
        """Update a container

        :param container: Either the id of a container or a
            :class:`~openstack.key_manager.v1.container.Container` instance.
        :param attrs: The attributes to update on the container represented
            by ``container``.

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
            :class:`~openstack.exceptions.NotFoundException` will be
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
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.key_manager.v1.order.Order` or None
        """
        return self._find(
            _order.Order, name_or_id, ignore_missing=ignore_missing
        )

    def get_order(self, order):
        """Get a single order

        :param order: The value can be the ID of an order or a
            :class:`~openstack.key_manager.v1.order.Order`
            instance.

        :returns: One :class:`~openstack.key_manager.v1.order.Order`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_order.Order, order)

    def orders(self, **query):
        """Return a generator of orders

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of order objects
        :rtype: :class:`~openstack.key_manager.v1.order.Order`
        """
        return self._list(_order.Order, **query)

    def update_order(self, order, **attrs):
        """Update a order

        :param order: Either the id of a order or a
            :class:`~openstack.key_manager.v1.order.Order` instance.
        :param attrs: The attributes to update on the order represented
            by ``order``.

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
            :class:`~openstack.exceptions.NotFoundException` will be
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
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.key_manager.v1.secret.Secret` or
            None
        """
        return self._find(
            _secret.Secret, name_or_id, ignore_missing=ignore_missing
        )

    def get_secret(self, secret):
        """Get a single secret

        :param secret: The value can be the ID of a secret or a
            :class:`~openstack.key_manager.v1.secret.Secret`
            instance.

        :returns: One :class:`~openstack.key_manager.v1.secret.Secret`
        :raises: :class:`~openstack.exceptions.NotFoundException`
            when no resource can be found.
        """
        return self._get(_secret.Secret, secret)

    def secrets(self, **query):
        """Return a generator of secrets

        :param kwargs query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of secret objects
        :rtype: :class:`~openstack.key_manager.v1.secret.Secret`
        """
        return self._list(_secret.Secret, **query)

    def update_secret(self, secret, **attrs):
        """Update a secret

        :param secret: Either the id of a secret or a
            :class:`~openstack.key_manager.v1.secret.Secret` instance.
        :param attrs: The attributes to update on the secret represented
            by ``secret``.

        :returns: The updated secret
        :rtype: :class:`~openstack.key_manager.v1.secret.Secret`
        """
        return self._update(_secret.Secret, secret, **attrs)

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
