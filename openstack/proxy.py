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

from openstack import exceptions
from openstack import resource


# The _check_resource decorator is used on BaseProxy methods to ensure that
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


class BaseProxy(object):

    def __init__(self, session):
        self._session = session

    def _get_resource(self, resource_type, value, path_args=None):
        """Get a resource object to work on

        :param resource_type: The type of resource to operate on. This should
                              be a subclass of
                              :class:`~openstack.resource.Resource` with a
                              ``from_id`` method.
        :param value: The ID of a resource or an object of ``resource_type``
                      class if using an existing instance, or None to create a
                      new instance.
        :param path_args: A dict containing arguments for forming the request
                          URL, if needed.
        """
        if value is None:
            # Create a bare resource
            res = resource_type()
        elif not isinstance(value, resource_type):
            # Create from an ID
            args = {resource_type.id_attribute:
                    resource.Resource.get_id(value)}
            res = resource_type.existing(**args)
        else:
            # An existing resource instance
            res = value

        # Set any intermediate path arguments, but don't overwrite Nones.
        if path_args is not None:
            res.update_attrs(ignore_none=True, **path_args)

        return res

    def _find(self, resource_type, name_or_id, path_args=None,
              ignore_missing=True):
        """Find a resource

        :param name_or_id: The name or ID of a resource to find.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.

        :returns: An instance of ``resource_type`` or None
        """
        return resource_type.find(self._session, name_or_id,
                                  path_args=path_args,
                                  ignore_missing=ignore_missing)

    @_check_resource(strict=False)
    def _delete(self, resource_type, value, path_args=None,
                ignore_missing=True):
        """Delete a resource

        :param resource_type: The type of resource to delete. This should
                              be a :class:`~openstack.resource.Resource`
                              subclass with a ``from_id`` method.
        :param value: The value to delete. Can be either the ID of a
                      resource or a :class:`~openstack.resource.Resource`
                      subclass.
        :param path_args: A dict containing arguments for forming the request
                          URL, if needed.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent resource.

        :returns: The result of the ``delete``
        :raises: ``ValueError`` if ``value`` is a
                 :class:`~openstack.resource.Resource` that doesn't match
                 the ``resource_type``.
                 :class:`~openstack.exceptions.ResourceNotFound` when
                 ignore_missing if ``False`` and a nonexistent resource
                 is attempted to be deleted.

        """
        res = self._get_resource(resource_type, value, path_args)

        try:
            rv = res.delete(self._session)
        except exceptions.NotFoundException as e:
            if ignore_missing:
                return None
            else:
                # Reraise with a more specific type and message
                raise exceptions.ResourceNotFound(
                    message="No %s found for %s" %
                            (resource_type.__name__, value),
                    details=e.details, response=e.response,
                    request_id=e.request_id, url=e.url, method=e.method,
                    http_status=e.http_status, cause=e.cause)

        return rv

    @_check_resource(strict=False)
    def _update(self, resource_type, value, path_args=None, **attrs):
        """Update a resource

        :param resource_type: The type of resource to update.
        :type resource_type: :class:`~openstack.resource.Resource`
        :param value: The resource to update. This must either be a
                      :class:`~openstack.resource.Resource` or an id
                      that corresponds to a resource.
        :param path_args: A dict containing arguments for forming the request
                          URL, if needed.
        :param **attrs: Attributes to update on a Resource object.
                        These attributes will be used in conjunction with
                        ``resource_type``.

        :returns: The result of the ``update``
        :rtype: :class:`~openstack.resource.Resource`
        """
        res = self._get_resource(resource_type, value, path_args)
        res.update_attrs(attrs)
        return res.update(self._session)

    def _create(self, resource_type, path_args=None, **attrs):
        """Create a resource from attributes

        :param resource_type: The type of resource to create.
        :type resource_type: :class:`~openstack.resource.Resource`
        :param path_args: A dict containing arguments for forming the request
                          URL, if needed.
        :param **attrs: Attributes from which to create a Resource object.
                        These attributes will be used in conjunction with
                        ``resource_type``.

        :returns: The result of the ``create``
        :rtype: :class:`~openstack.resource.Resource`
        """
        res = resource_type.new(**attrs)
        if path_args is not None:
            res.update_attrs(path_args)
        return res.create(self._session)

    @_check_resource(strict=False)
    def _get(self, resource_type, value=None, path_args=None, args=None):
        """Get a resource

        :param resource_type: The type of resource to get.
        :type resource_type: :class:`~openstack.resource.Resource`
        :param value: The value to get. Can be either the ID of a
                      resource or a :class:`~openstack.resource.Resource`
                      subclass.
        :param path_args: A dict containing arguments for forming the request
                          URL, if needed.
        :param args: A optional dict containing arguments that will be
            translated into query strings when forming the request URL.

        :returns: The result of the ``get``
        :rtype: :class:`~openstack.resource.Resource`
        """
        res = self._get_resource(resource_type, value, path_args)

        try:
            return res.get(self._session, args=args)
        except exceptions.NotFoundException as e:
            raise exceptions.ResourceNotFound(
                message="No %s found for %s" %
                        (resource_type.__name__, value),
                details=e.details, response=e.response,
                request_id=e.request_id, url=e.url, method=e.method,
                http_status=e.http_status, cause=e.cause)

    def _list(self, resource_type, value=None, paginated=False,
              path_args=None, **query):
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
        :param path_args: A dictionary containing arguments for use when
                          forming the request URL for resource retrieval.
        :param kwargs **query: Keyword arguments that are sent to the list
                               method, which are then attached as query
                               parameters on the request URL.

        :returns: A generator of Resource objects.
        :raises: ``ValueError`` if ``value`` is a
                 :class:`~openstack.resource.Resource` that doesn't match
                 the ``resource_type``.
        """
        res = self._get_resource(resource_type, value, path_args)

        query = res.convert_ids(query)
        return res.list(self._session, path_args=path_args,
                        paginated=paginated, params=query)

    def _head(self, resource_type, value=None, path_args=None):
        """Retrieve a resource's header

        :param resource_type: The type of resource to retrieve.
        :type resource_type: :class:`~openstack.resource.Resource`
        :param value: The value of a specific resource to retreive headers
                      for. Can be either the ID of a resource,
                      a :class:`~openstack.resource.Resource` subclass,
                      or ``None``.
        :param path_args: A dict containing arguments for forming the request
                          URL, if needed.

        :returns: The result of the ``head`` call
        :rtype: :class:`~openstack.resource.Resource`
        """
        res = self._get_resource(resource_type, value, path_args)

        return res.head(self._session)

    def wait_for_status(self, value, status, failures=[], interval=2,
                        wait=120):
        """Wait for a resource to be in a particular status.

        :param value: The resource to wait on to reach the status. The
                      resource must have a status attribute.
        :type value: :class:`~openstack.resource.Resource`
        :param status: Desired status of the resource.
        :param list failures: Statuses that would indicate the transition
                              failed such as 'ERROR'.
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for the change.

        :return: Method returns resource on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` transition
                 to status failed to occur in wait seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` resource
                 transitioned to one of the failure states.
        :raises: :class:`~AttributeError` if the resource does not have a
                 status attribute
        """
        return resource.wait_for_status(self._session, value, status,
                                        failures, interval, wait)

    def wait_for_delete(self, value, interval=2, wait=120):
        """Wait for the resource to be deleted.

        :param value: The resource to wait on to be deleted.
        :type value: :class:`~openstack.resource.Resource`
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for the delete.

        :return: Method returns resource on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` transition
                 to delete failed to occur in wait seconds.
        """
        return resource.wait_for_delete(self._session, value, interval, wait)
