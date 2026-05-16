# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from collections.abc import Callable, Generator
from typing import Any, ClassVar, Literal, overload
import warnings

from openstack.placement.v1 import resource_class as _resource_class
from openstack.placement.v1 import resource_provider as _resource_provider
from openstack.placement.v1 import (
    resource_provider_inventory as _resource_provider_inventory,
)
from openstack.placement.v1 import trait as _trait
from openstack import proxy
from openstack import resource
from openstack import warnings as os_warnings


class Proxy(proxy.Proxy):
    api_version: ClassVar[Literal['1']] = '1'

    _resource_registry = {
        "resource_class": _resource_class.ResourceClass,
        "resource_provider": _resource_provider.ResourceProvider,
    }

    # resource classes

    def create_resource_class(
        self, **attrs: Any
    ) -> _resource_class.ResourceClass:
        """Create a new resource class from attributes.

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.placement.v1.resource_provider.ResourceClass`,
            comprised of the properties on the ResourceClass class.

        :returns: The results of resource class creation
        """
        return self._create(_resource_class.ResourceClass, **attrs)

    def delete_resource_class(
        self,
        resource_class: str | _resource_class.ResourceClass,
        ignore_missing: bool = True,
    ) -> None:
        """Delete a resource class

        :param resource_class: The value can be either the ID of a resource
            class or an
            :class:`~openstack.placement.v1.resource_class.ResourceClass`,
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the resource class does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            resource class.

        :returns: ``None``
        """
        self._delete(
            _resource_class.ResourceClass,
            resource_class,
            ignore_missing=ignore_missing,
        )

    def update_resource_class(
        self, resource_class: str | _resource_class.ResourceClass, **attrs: Any
    ) -> _resource_class.ResourceClass:
        """Update a resource class

        :param resource_class: The value can be either the ID of a resource
            class or an
            :class:`~openstack.placement.v1.resource_class.ResourceClass`,
            instance.
        :param attrs: The attributes to update on the resource class
            represented by ``resource_class``.

        :returns: The updated resource class
        """
        return self._update(
            _resource_class.ResourceClass,
            resource_class,
            **attrs,
        )

    def get_resource_class(
        self,
        resource_class: str | _resource_class.ResourceClass,
    ) -> _resource_class.ResourceClass:
        """Get a single resource_class.

        :param resource_class: The value can be either the ID of a resource
            class or an
            :class:`~openstack.placement.v1.resource_class.ResourceClass`,
            instance.

        :returns: An instance of
            :class:`~openstack.placement.v1.resource_class.ResourceClass`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource class matching the criteria could be found.
        """
        return self._get(
            _resource_class.ResourceClass,
            resource_class,
        )

    def resource_classes(
        self,
        **query: Any,
    ) -> Generator[_resource_class.ResourceClass, None, None]:
        """Retrieve a generator of resource classs.

        :param query: Optional query parameters to be sent to
            restrict the resource classs to be returned.

        :returns: A generator of resource class instances.
        """
        return self._list(_resource_class.ResourceClass, **query)

    # resource providers

    def create_resource_provider(
        self, **attrs: Any
    ) -> _resource_provider.ResourceProvider:
        """Create a new resource provider from attributes.

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`,
            comprised of the properties on the ResourceProvider class.

        :returns: The results of resource provider creation
        """
        return self._create(_resource_provider.ResourceProvider, **attrs)

    def delete_resource_provider(
        self,
        resource_provider: str | _resource_provider.ResourceProvider,
        ignore_missing: bool = True,
    ) -> None:
        """Delete a resource provider

        :param resource_provider: The value can be either the ID of a resource
            provider or an
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`,
            instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the resource provider does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            resource provider.

        :returns: ``None``
        """
        self._delete(
            _resource_provider.ResourceProvider,
            resource_provider,
            ignore_missing=ignore_missing,
        )

    def update_resource_provider(
        self,
        resource_provider: str | _resource_provider.ResourceProvider,
        **attrs: Any,
    ) -> _resource_provider.ResourceProvider:
        """Update a resource provider

        :param resource_provider: The value can be either the ID of a resource
            provider or an
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`,
            instance.
        :param attrs: The attributes to update on the resource provider
            represented by ``resource_provider``.

        :returns: The updated resource provider
        """
        return self._update(
            _resource_provider.ResourceProvider,
            resource_provider,
            **attrs,
        )

    def get_resource_provider(
        self,
        resource_provider: str | _resource_provider.ResourceProvider,
    ) -> _resource_provider.ResourceProvider:
        """Get a single resource_provider.

        :param resource_provider: The value can be either the ID of a resource
            provider or an
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`,
            instance.

        :returns: An instance of
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource provider matching the criteria could be found.
        """
        return self._get(
            _resource_provider.ResourceProvider,
            resource_provider,
        )

    @overload
    def find_resource_provider(
        self,
        name_or_id: str,
        ignore_missing: Literal[False],
    ) -> _resource_provider.ResourceProvider: ...

    @overload
    def find_resource_provider(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _resource_provider.ResourceProvider | None: ...

    def find_resource_provider(
        self,
        name_or_id: str,
        ignore_missing: bool = True,
    ) -> _resource_provider.ResourceProvider | None:
        """Find a single resource_provider.

        :param name_or_id: The name or ID of a resource provider.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the resource does not exist.  When set to ``True``, None will
            be returned when attempting to find a nonexistent resource.

        :returns: An instance of
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource provider matching the criteria could be found.
        """
        return self._find(
            _resource_provider.ResourceProvider,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def resource_providers(
        self,
        **query: Any,
    ) -> Generator[_resource_provider.ResourceProvider, None, None]:
        """Retrieve a generator of resource providers.

        :param query: Optional query parameters to be sent to
            restrict the resource providers to be returned.

        :returns: A generator of resource provider instances.
        """
        return self._list(_resource_provider.ResourceProvider, **query)

    # resource provider aggregates

    def fetch_resource_provider_aggregates(
        self,
        resource_provider: str | _resource_provider.ResourceProvider,
    ) -> _resource_provider.ResourceProvider:
        """Get a list of aggregates for a resource provider.

        :param resource_provider: The value can be either the ID of a resource
            provider or an
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`,
            instance.

        :returns: An instance of
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
            with the ``aggregates`` attribute populated.
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource provider matching the criteria could be found.
        """
        res = self._get_resource(
            _resource_provider.ResourceProvider,
            resource_provider,
        )
        return res.fetch_aggregates(self)

    # TODO(stephenfin): Remove in 5.0
    def get_resource_provider_aggregates(
        self,
        resource_provider: str | _resource_provider.ResourceProvider,
    ) -> _resource_provider.ResourceProvider:
        """Get a list of aggregates for a resource provider.

        .. deprecated:: 4.14.0
            Use :meth:`fetch_resource_provider_aggregates` instead.
        """
        warnings.warn(
            "The 'get_resource_provider_aggregates' method is deprecated; "
            "use 'fetch_resource_provider_aggregates' instead.",
            os_warnings.RemovedInSDK50Warning,
        )
        return self.fetch_resource_provider_aggregates(resource_provider)

    def set_resource_provider_aggregates(self, resource_provider, *aggregates):
        """Update aggregates for a resource provider.

        :param resource_provider: The value can be either the ID of a resource
            provider or an
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`,
            instance.
        :param aggregates: A list of aggregates. These aggregates will replace
            all aggregates currently present.

        :returns: An instance of
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
            with the ``aggregates`` attribute populated with the updated value.
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource provider matching the criteria could be found.
        """
        res = self._get_resource(
            _resource_provider.ResourceProvider,
            resource_provider,
        )
        return res.set_aggregates(self, aggregates=aggregates)

    # resource provider inventories

    def create_resource_provider_inventory(
        self,
        resource_provider: str | _resource_provider.ResourceProvider,
        resource_class: str | _resource_class.ResourceClass,
        *,
        total: int,
        **attrs: Any,
    ) -> _resource_provider_inventory.ResourceProviderInventory:
        """Create a new resource provider inventory from attributes

        :param resource_provider: Either the ID of a resource provider or a
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
            instance.
        :param resource_class: The value can be either the ID of a resource
            class or an
            :class:`~openstack.placement.v1.resource_class.ResourceClass`,
            instance.
        :param total: The actual amount of the resource that the provider can
            accommodate.
        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.placement.v1.resource_provider_inventory.ResourceProviderInventory`,
            comprised of the properties on the ResourceProviderInventory class.

        :returns: The results of resource provider inventory creation
        """
        resource_provider_id = resource.Resource._get_id(resource_provider)
        resource_class_name = resource.Resource._get_id(resource_class)
        return self._create(
            _resource_provider_inventory.ResourceProviderInventory,
            resource_provider_id=resource_provider_id,
            resource_class=resource_class_name,
            total=total,
            **attrs,
        )

    def delete_resource_provider_inventory(
        self,
        resource_provider_inventory: str
        | _resource_provider_inventory.ResourceProviderInventory,
        resource_provider: str
        | _resource_provider.ResourceProvider
        | None = None,
        ignore_missing: bool = True,
    ) -> None:
        """Delete a resource provider inventory

        :param resource_provider_inventory: The value can be either the ID of a
            resource provider or an
            :class:`~openstack.placement.v1.resource_provider_inventory.ResourceProviderInventory`,
            instance.
        :param resource_provider: Either the ID of a resource provider or a
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
            instance. This value must be specified when
            ``resource_provider_inventory`` is an ID.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the resource provider inventory does not exist. When set to
            ``True``, no exception will be set when attempting to delete a
            nonexistent resource provider inventory.

        :returns: ``None``
        """
        resource_provider_id = self._get_uri_attribute(
            resource_provider_inventory,
            resource_provider,
            'resource_provider_id',
        )
        self._delete(
            _resource_provider_inventory.ResourceProviderInventory,
            resource_provider_inventory,
            resource_provider_id=resource_provider_id,
            ignore_missing=ignore_missing,
        )

    def update_resource_provider_inventory(
        self,
        resource_provider_inventory: str
        | _resource_provider_inventory.ResourceProviderInventory,
        resource_provider: str
        | _resource_provider.ResourceProvider
        | None = None,
        *,
        resource_provider_generation: int | None = None,
        **attrs: Any,
    ) -> _resource_provider_inventory.ResourceProviderInventory:
        """Update a resource provider's inventory

        :param resource_provider_inventory: The value can be either the ID of a resource
            provider inventory or an
            :class:`~openstack.placement.v1.resource_provider_inventory.ResourceProviderInventory`,
            instance.
        :param resource_provider: Either the ID of a resource provider or a
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
            instance. This value must be specified when
            ``resource_provider_inventory`` is an ID.
        :attrs kwargs: The attributes to update on the resource provider inventory
            represented by ``resource_provider_inventory``.

        :returns: The updated resource provider inventory
        """  # noqa: E501
        resource_provider_id = self._get_uri_attribute(
            resource_provider_inventory,
            resource_provider,
            'resource_provider_id',
        )
        return self._update(
            _resource_provider_inventory.ResourceProviderInventory,
            resource_provider_inventory,
            resource_provider_id=resource_provider_id,
            resource_provider_generation=resource_provider_generation,
            **attrs,
        )

    def get_resource_provider_inventory(
        self,
        resource_provider_inventory: (
            str | _resource_provider_inventory.ResourceProviderInventory
        ),
        resource_provider: (
            str | _resource_provider.ResourceProvider | None
        ) = None,
    ) -> _resource_provider_inventory.ResourceProviderInventory:
        """Get a single resource_provider_inventory

        :param resource_provider_inventory: The value can be either the ID of a
            resource provider inventory or an
            :class:`~openstack.placement.v1.resource_provider_inventory.ResourceProviderInventory`,
            instance.
        :param resource_provider: Either the ID of a resource provider or a
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
            instance. This value must be specified when
            ``resource_provider_inventory`` is an ID.

        :returns: An instance of
            :class:`~openstack.placement.v1.resource_provider_inventory.ResourceProviderInventory`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource provider inventory matching the criteria could be found.
        """
        resource_provider_id = self._get_uri_attribute(
            resource_provider_inventory,
            resource_provider,
            'resource_provider_id',
        )
        return self._get(
            _resource_provider_inventory.ResourceProviderInventory,
            resource_provider_inventory,
            resource_provider_id=resource_provider_id,
        )

    def resource_provider_inventories(
        self,
        resource_provider: str | _resource_provider.ResourceProvider,
        **query: Any,
    ) -> Generator[
        _resource_provider_inventory.ResourceProviderInventory, None, None
    ]:
        """Retrieve a generator of resource provider inventories

        :param resource_provider: Either the ID of a resource provider or a
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
            instance.
        :param query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of resource provider inventory instances.
        """
        resource_provider_id = resource.Resource._get_id(resource_provider)
        return self._list(
            _resource_provider_inventory.ResourceProviderInventory,
            resource_provider_id=resource_provider_id,
            **query,
        )

    # ========== Traits ==========

    def create_trait(self, name: str) -> _trait.Trait:
        """Create a new trait

        :param name: The name of the new trait

        :returns: The results of trait creation
        """
        return self._create(_trait.Trait, name=name)

    def delete_trait(
        self, trait: str | _trait.Trait, ignore_missing: bool = True
    ) -> None:
        """Delete a trait

        :param trait: The value can be either the ID of a trait or an
            :class:`~openstack.placement.v1.trait.Trait`, instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the resource provider inventory does not exist. When set to
            ``True``, no exception will be set when attempting to delete a
            nonexistent resource provider inventory.

        :returns: ``None``
        """
        self._delete(_trait.Trait, trait, ignore_missing=ignore_missing)

    def get_trait(self, trait: str | _trait.Trait) -> _trait.Trait:
        """Get a single trait

        :param trait: The value can be either the ID of a trait or an
            :class:`~openstack.placement.v1.trait.Trait`, instance.

        :returns: An instance of
            :class:`~openstack.placement.v1.resource_provider_inventory.ResourceProviderInventory`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            trait matching the criteria could be found.
        """
        return self._get(_trait.Trait, trait)

    def traits(self, **query: Any) -> Generator[_trait.Trait, None, None]:
        """Retrieve a generator of traits

        :param query: Optional query parameters to be sent to limit
            the resources being returned.

        :returns: A generator of trait objects
        """
        return self._list(_trait.Trait, **query)

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: list[str] | None = None,
        interval: int | float | None = 2,
        wait: int | None = None,
        attribute: str = 'status',
        callback: Callable[[int], None] | None = None,
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

        :returns: The updated resource.
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
        interval: int | float | None = 2,
        wait: int | None = 120,
        callback: Callable[[int], None] | None = None,
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
