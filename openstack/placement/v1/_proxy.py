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

from openstack.placement.v1 import resource_class as _resource_class
from openstack.placement.v1 import resource_provider as _resource_provider
from openstack import proxy


class Proxy(proxy.Proxy):

    # resource classes

    def create_resource_class(self, **attrs):
        """Create a new resource class from attributes.

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.placement.v1.resource_provider.ResourceClass`,
            comprised of the properties on the ResourceClass class.

        :returns: The results of resource class creation
        :rtype: :class:`~openstack.placement.v1.resource_class.ResourceClass`
        """
        return self._create(_resource_class.ResourceClass, **attrs)

    def delete_resource_class(self, resource_class, ignore_missing=True):
        """Delete a resource class

        :param resource_class: The value can be either the ID of a resource
            class or an
            :class:`~openstack.placement.v1.resource_class.ResourceClass`,
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the resource class does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            resource class.

        :returns: ``None``
        """
        self._delete(
            _resource_class.ResourceClass,
            resource_class,
            ignore_missing=ignore_missing,
        )

    def update_resource_class(self, resource_class, **attrs):
        """Update a resource class

        :param resource_class: The value can be either the ID of a resource
            class or an
            :class:`~openstack.placement.v1.resource_class.ResourceClass`,
            instance.
        :param attrs: The attributes to update on the resource class
            represented by ``resource_class``.

        :returns: The updated resource class
        :rtype: :class:`~openstack.placement.v1.resource_class.ResourceClass`
        """
        return self._update(
            _resource_class.ResourceClass, resource_class, **attrs,
        )

    def get_resource_class(self, resource_class):
        """Get a single resource_class.

        :param resource_class: The value can be either the ID of a resource
            class or an
            :class:`~openstack.placement.v1.resource_class.ResourceClass`,
            instance.

        :returns: An instance of
            :class:`~openstack.placement.v1.resource_class.ResourceClass`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            resource class matching the criteria could be found.
        """
        return self._get(
            _resource_class.ResourceClass, resource_class,
        )

    def resource_classes(self, **query):
        """Retrieve a generator of resource classs.

        :param kwargs query: Optional query parameters to be sent to
            restrict the resource classs to be returned.

        :returns: A generator of resource class instances.
        """
        return self._list(_resource_class.ResourceClass, **query)

    # resource providers

    def create_resource_provider(self, **attrs):
        """Create a new resource provider from attributes.

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`,
            comprised of the properties on the ResourceProvider class.

        :returns: The results of resource provider creation
        :rtype: :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
        """  # noqa: E501
        return self._create(_resource_provider.ResourceProvider, **attrs)

    def delete_resource_provider(self, resource_provider, ignore_missing=True):
        """Delete a resource provider

        :param resource_provider: The value can be either the ID of a resource
            provider or an
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`,
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the resource provider does not exist. When set to ``True``, no
            exception will be set when attempting to delete a nonexistent
            resource provider.

        :returns: ``None``
        """
        self._delete(
            _resource_provider.ResourceProvider,
            resource_provider,
            ignore_missing=ignore_missing,
        )

    def update_resource_provider(self, resource_provider, **attrs):
        """Update a resource provider

        :param resource_provider: The value can be either the ID of a resource
            provider or an
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`,
            instance.
        :param attrs: The attributes to update on the resource provider
            represented by ``resource_provider``.

        :returns: The updated resource provider
        :rtype: :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
        """  # noqa: E501
        return self._update(
            _resource_provider.ResourceProvider, resource_provider, **attrs,
        )

    def get_resource_provider(self, resource_provider):
        """Get a single resource_provider.

        :param resource_provider: The value can be either the ID of a resource
            provider or an
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`,
            instance.

        :returns: An instance of
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            resource provider matching the criteria could be found.
        """
        return self._get(
            _resource_provider.ResourceProvider, resource_provider,
        )

    def find_resource_provider(self, name_or_id, ignore_missing=True):
        """Find a single resource_provider.

        :param name_or_id: The name or ID of a resource provider.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be raised when
            the resource does not exist.  When set to ``True``, None will be
            returned when attempting to find a nonexistent resource.

        :returns: An instance of
            :class:`~openstack.placement.v1.resource_provider.ResourceProvider`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            resource provider matching the criteria could be found.
        """
        return self._find(
            _resource_provider.ResourceProvider,
            name_or_id,
            ignore_missing=ignore_missing,
        )

    def resource_providers(self, **query):
        """Retrieve a generator of resource providers.

        :param kwargs query: Optional query parameters to be sent to
            restrict the resource providers to be returned.

        :returns: A generator of resource provider instances.
        """
        return self._list(_resource_provider.ResourceProvider, **query)
