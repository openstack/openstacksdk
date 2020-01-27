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

from openstack import _adapter
from openstack import exceptions
from openstack import resource


# The _check_resource decorator is used on Proxy methods to ensure that
# the `actual` argument is in fact the type of the `expected` argument.
# It does so under two cases:
# 1. When strict=False, if and only if `actual` is a Resource instance,
#    it is checked to see that it's an instance of the `expected` class.
#    This allows `actual` to be other types, such as strings, when it makes
#    sense to accept a raw id value.
# 2. When strict=True, `actual` must be an instance of the `expected` class.
def _check_resource(strict=False):
    def wrap(method):
        def check(self, expected, actual=None, *args, **kwargs):
            if (strict and actual is not None and not
               isinstance(actual, resource.Resource)):
                raise ValueError("A %s must be passed" % expected.__name__)
            elif (isinstance(actual, resource.Resource) and not
                  isinstance(actual, expected)):
                raise ValueError("Expected %s but received %s" % (
                                 expected.__name__, actual.__class__.__name__))

            return method(self, expected, actual, *args, **kwargs)
        return check
    return wrap


class Proxy(_adapter.OpenStackSDKAdapter):
    """Represents a service."""

    retriable_status_codes = None
    """HTTP status codes that should be retried by default.

    The number of retries is defined by the configuration in parameters called
    ``<service-type>_status_code_retries``.
    """

    def __init__(self, *args, **kwargs):
        # NOTE(dtantsur): keystoneauth defaults retriable_status_codes to None,
        # override it with a class-level value.
        kwargs.setdefault('retriable_status_codes',
                          self.retriable_status_codes)
        super(Proxy, self).__init__(*args, **kwargs)

    def _get_connection(self):
        """Get the Connection object associated with this Proxy.

        When the Session is created, a reference to the Connection is attached
        to the ``_sdk_connection`` attribute. We also add a reference to it
        directly on ourselves. Use one of them.
        """
        return getattr(
            self, '_connection', getattr(
                self.session, '_sdk_connection', None))

    def _get_resource(self, resource_type, value, **attrs):
        """Get a resource object to work on

        :param resource_type: The type of resource to operate on. This should
                              be a subclass of
                              :class:`~openstack.resource.Resource` with a
                              ``from_id`` method.
        :param value: The ID of a resource or an object of ``resource_type``
                      class if using an existing instance, or ``munch.Munch``,
                      or None to create a new instance.
        :param path_args: A dict containing arguments for forming the request
                          URL, if needed.
        """
        conn = self._get_connection()
        if value is None:
            # Create a bare resource
            res = resource_type.new(connection=conn, **attrs)
        elif (isinstance(value, dict)
              and not isinstance(value, resource.Resource)):
            res = resource_type._from_munch(
                value, connection=conn)
            res._update(**attrs)
        elif not isinstance(value, resource_type):
            # Create from an ID
            res = resource_type.new(
                id=value, connection=conn, **attrs)
        else:
            # An existing resource instance
            res = value
            res._update(**attrs)

        return res

    def _get_uri_attribute(self, child, parent, name):
        """Get a value to be associated with a URI attribute

        `child` will not be None here as it's a required argument
        on the proxy method. `parent` is allowed to be None if `child`
        is an actual resource, but when an ID is given for the child
        one must also be provided for the parent. An example of this
        is that a parent is a Server and a child is a ServerInterface.
        """
        if parent is None:
            value = getattr(child, name)
        else:
            value = resource.Resource._get_id(parent)
        return value

    def _find(self, resource_type, name_or_id, ignore_missing=True,
              **attrs):
        """Find a resource

        :param name_or_id: The name or ID of a resource to find.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict attrs: Attributes to be passed onto the
                           :meth:`~openstack.resource.Resource.find`
                           method, such as query parameters.

        :returns: An instance of ``resource_type`` or None
        """
        return resource_type.find(self, name_or_id,
                                  ignore_missing=ignore_missing,
                                  **attrs)

    @_check_resource(strict=False)
    def _delete(self, resource_type, value, ignore_missing=True, **attrs):
        """Delete a resource

        :param resource_type: The type of resource to delete. This should
                              be a :class:`~openstack.resource.Resource`
                              subclass with a ``from_id`` method.
        :param value: The value to delete. Can be either the ID of a
                      resource or a :class:`~openstack.resource.Resource`
                      subclass.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent resource.
        :param dict attrs: Attributes to be passed onto the
                           :meth:`~openstack.resource.Resource.delete`
                           method, such as the ID of a parent resource.

        :returns: The result of the ``delete``
        :raises: ``ValueError`` if ``value`` is a
                 :class:`~openstack.resource.Resource` that doesn't match
                 the ``resource_type``.
                 :class:`~openstack.exceptions.ResourceNotFound` when
                 ignore_missing if ``False`` and a nonexistent resource
                 is attempted to be deleted.

        """
        res = self._get_resource(resource_type, value, **attrs)

        try:
            rv = res.delete(self)
        except exceptions.ResourceNotFound:
            if ignore_missing:
                return None
            raise

        return rv

    @_check_resource(strict=False)
    def _update(self, resource_type, value, base_path=None, **attrs):
        """Update a resource

        :param resource_type: The type of resource to update.
        :type resource_type: :class:`~openstack.resource.Resource`
        :param value: The resource to update. This must either be a
                      :class:`~openstack.resource.Resource` or an id
                      that corresponds to a resource.
        :param str base_path: Base part of the URI for updating resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.
        :param dict attrs: Attributes to be passed onto the
                           :meth:`~openstack.resource.Resource.update`
                           method to be updated. These should correspond
                           to either :class:`~openstack.resource.Body`
                           or :class:`~openstack.resource.Header`
                           values on this resource.

        :returns: The result of the ``update``
        :rtype: :class:`~openstack.resource.Resource`
        """
        res = self._get_resource(resource_type, value, **attrs)
        return res.commit(self, base_path=base_path)

    def _create(self, resource_type, base_path=None, **attrs):
        """Create a resource from attributes

        :param resource_type: The type of resource to create.
        :type resource_type: :class:`~openstack.resource.Resource`
        :param str base_path: Base part of the URI for creating resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.
        :param path_args: A dict containing arguments for forming the request
                          URL, if needed.
        :param dict attrs: Attributes to be passed onto the
                           :meth:`~openstack.resource.Resource.create`
                           method to be created. These should correspond
                           to either :class:`~openstack.resource.Body`
                           or :class:`~openstack.resource.Header`
                           values on this resource.

        :returns: The result of the ``create``
        :rtype: :class:`~openstack.resource.Resource`
        """
        conn = self._get_connection()
        res = resource_type.new(connection=conn, **attrs)
        return res.create(self, base_path=base_path)

    @_check_resource(strict=False)
    def _get(self, resource_type, value=None, requires_id=True,
             base_path=None, **attrs):
        """Fetch a resource

        :param resource_type: The type of resource to get.
        :type resource_type: :class:`~openstack.resource.Resource`
        :param value: The value to get. Can be either the ID of a
                      resource or a :class:`~openstack.resource.Resource`
                      subclass.
        :param str base_path: Base part of the URI for fetching resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.
        :param dict attrs: Attributes to be passed onto the
                           :meth:`~openstack.resource.Resource.get`
                           method. These should correspond
                           to either :class:`~openstack.resource.Body`
                           or :class:`~openstack.resource.Header`
                           values on this resource.

        :returns: The result of the ``fetch``
        :rtype: :class:`~openstack.resource.Resource`
        """
        res = self._get_resource(resource_type, value, **attrs)

        return res.fetch(
            self, requires_id=requires_id, base_path=base_path,
            error_message="No {resource_type} found for {value}".format(
                resource_type=resource_type.__name__, value=value))

    def _list(self, resource_type, value=None,
              paginated=True, base_path=None, **attrs):
        """List a resource

        :param resource_type: The type of resource to delete. This should
                              be a :class:`~openstack.resource.Resource`
                              subclass with a ``from_id`` method.
        :param value: The resource to list. It can be the ID of a resource, or
                      a :class:`~openstack.resource.Resource` object. When set
                      to None, a new bare resource is created.
        :param bool paginated: When set to ``False``, expect all of the data
                               to be returned in one response. When set to
                               ``True``, the resource supports data being
                               returned across multiple pages.
        :param str base_path: Base part of the URI for listing resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.
        :param dict attrs: Attributes to be passed onto the
            :meth:`~openstack.resource.Resource.list` method. These should
            correspond to either :class:`~openstack.resource.URI` values
            or appear in :data:`~openstack.resource.Resource._query_mapping`.

        :returns: A generator of Resource objects.
        :raises: ``ValueError`` if ``value`` is a
                 :class:`~openstack.resource.Resource` that doesn't match
                 the ``resource_type``.
        """
        return resource_type.list(
            self, paginated=paginated,
            base_path=base_path,
            **attrs)

    def _head(self, resource_type, value=None, base_path=None, **attrs):
        """Retrieve a resource's header

        :param resource_type: The type of resource to retrieve.
        :type resource_type: :class:`~openstack.resource.Resource`
        :param value: The value of a specific resource to retreive headers
                      for. Can be either the ID of a resource,
                      a :class:`~openstack.resource.Resource` subclass,
                      or ``None``.
        :param str base_path: Base part of the URI for heading resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.
        :param dict attrs: Attributes to be passed onto the
                           :meth:`~openstack.resource.Resource.head` method.
                           These should correspond to
                           :class:`~openstack.resource.URI` values.

        :returns: The result of the ``head`` call
        :rtype: :class:`~openstack.resource.Resource`
        """
        res = self._get_resource(resource_type, value, **attrs)
        return res.head(self, base_path=base_path)
