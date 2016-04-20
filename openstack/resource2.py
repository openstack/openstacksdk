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

"""
The :class:`~openstack.resource.Resource` class is a base
class that represent a remote resource. The attributes that
comprise a request or response for this resource are specified
as class members on the Resource subclass where their values
are of a component type, including :class:`~openstack.resource2.Body`,
:class:`~openstack.resource2.Header`, and :class:`~openstack.resource2.URI`.

For update management, :class:`~openstack.resource2.Resource` employs
a series of :class:`~openstack.resource2._ComponentManager` instances
to look after the attributes of that particular component type. This is
particularly useful for Body and Header types, so that only the values
necessary are sent in requests to the server.

When making requests, each of the managers are looked at to gather the
necessary URI, body, and header data to build a request to be sent
via keystoneauth's sessions. Responses from keystoneauth are then
converted into this Resource class' appropriate components and types
and then returned to the caller.
"""

import collections
import itertools
import time

from openstack import exceptions
from openstack import format
from openstack import utils


class _BaseComponent(object):

    # The name this component is being tracked as in the Resource
    key = None

    def __init__(self, name, type=None, default=None, alternate_id=False):
        """A typed descriptor for a component that makes up a Resource

        :param name: The name this component exists as on the server
        :param type: The type this component is expected to be by the server.
                     By default this is None, meaning any value you specify
                     will work. If you specify type=dict and then set a
                     component to a string, __set__ will fail, for example.
        :param default: Typically None, but any other default can be set.
        :param alternate_id: When `True`, this property is known
                             internally as a value that can be sent
                             with requests that require an ID but
                             when `id` is not a name the Resource has.
                             This is a relatively uncommon case, and this
                             setting should only be used once per Resource.
        """
        self.name = name
        self.type = type
        self.default = default
        self.alternate_id = alternate_id

    def __get__(self, instance, owner):
        if instance is None:
            return None

        attributes = getattr(instance, self.key)

        try:
            value = attributes[self.name]
        except KeyError:
            return self.default

        # self.type() should not be called on None objects.
        if value is None:
            return None

        if self.type and not isinstance(value, self.type):
            if issubclass(self.type, format.Formatter):
                value = self.type.deserialize(value)
            else:
                value = self.type(value)

        return value

    def __set__(self, instance, value):
        if (self.type and not isinstance(value, self.type) and
                value != self.default):
            if issubclass(self.type, format.Formatter):
                value = self.type.serialize(value)
            else:
                value = str(self.type(value))  # validate to fail fast

        attributes = getattr(instance, self.key)
        attributes[self.name] = value

    def __delete__(self, instance):
        try:
            attributes = getattr(instance, self.key)
            del attributes[self.name]
        except KeyError:
            pass


class Body(_BaseComponent):
    """Body attributes"""

    key = "_body"


class Header(_BaseComponent):
    """Header attributes"""

    key = "_header"


class URI(_BaseComponent):
    """URI attributes"""

    key = "_uri"


class _ComponentManager(collections.MutableMapping):
    """Storage of a component type"""

    def __init__(self, attributes=None, synchronized=False):
        self.attributes = dict() if attributes is None else attributes.copy()
        self._dirty = set() if synchronized else set(self.attributes.keys())

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        try:
            orig = self.attributes[key]
        except KeyError:
            changed = True
        else:
            changed = orig != value

        if changed:
            self.attributes[key] = value
            self._dirty.add(key)

    def __delitem__(self, key):
        del self.attributes[key]
        self._dirty.add(key)

    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)

    @property
    def dirty(self):
        """Return a dict of modified attributes"""
        return dict((key, self.attributes.get(key, None))
                    for key in self._dirty)

    def clean(self):
        """Signal that the resource no longer has modified attributes"""
        self._dirty = set()


class _Request(object):
    """Prepared components that go into a KSA request"""

    def __init__(self, uri, body, headers):
        self.uri = uri
        self.body = body
        self.headers = headers


class QueryParameters(object):

    def __init__(self, *names, **mappings):
        """Create a dict of accepted query parameters

        names are strings where the client-side name matches
        what the server expects, e.g., server=server.

        mappings are key-value pairs where the key is the
        client-side name we'll accept here and the value is
        the name the server expects, e.g, changes_since=changes-since
        """
        self._mapping = dict({name: name for name in names}, **mappings)

    def _transpose(self, query):
        """Transpose the keys in query based on the mapping

        This method converts the keys in `query` from their
        client-side names to have the appropriate keys as
        expected by the server for query parameters.
        """
        result = {}
        for key, value in self._mapping.items():
            if key in query:
                result[value] = query[key]
        return result


class Resource(object):

    #: Singular form of key for resource.
    resource_key = None
    #: Plural form of key for resource.
    resources_key = None

    #: The ID of this resource.
    id = Body("id")
    #: The name of this resource.
    name = Body("name")
    #: The location of this resource.
    location = Header("location")

    #: Mapping of accepted query parameter names.
    _query_mapping = QueryParameters()

    #: The base part of the URI for this resource.
    base_path = ""

    #: The service associated with this resource to find the service URL.
    service = None

    #: Allow create operation for this resource.
    allow_create = False
    #: Allow get operation for this resource.
    allow_get = False
    #: Allow update operation for this resource.
    allow_update = False
    #: Allow delete operation for this resource.
    allow_delete = False
    #: Allow list operation for this resource.
    allow_list = False
    #: Allow head operation for this resource.
    allow_head = False
    #: Use PATCH for update operations on this resource.
    patch_update = False

    def __init__(self, synchronized=False, **attrs):
        # NOTE: _collect_attrs modifies **attrs in place, removing
        # items as they match up with any of the body, header,
        # or uri mappings.
        body, header, uri = self._collect_attrs(attrs)
        # TODO(briancurtin): at this point if attrs has anything left
        # they're not being set anywhere. Log this? Raise exception?
        # How strict should we be here? Should strict be an option?

        self._body = _ComponentManager(attributes=body,
                                       synchronized=synchronized)
        self._header = _ComponentManager(attributes=header,
                                         synchronized=synchronized)
        self._uri = _ComponentManager(attributes=uri,
                                      synchronized=synchronized)

    def __repr__(self):
        pairs = ["%s=%s" % (k, v) for k, v in dict(itertools.chain(
            self._body.attributes.items(),
            self._header.attributes.items(),
            self._uri.attributes.items())).items()]
        args = ", ".join(pairs)

        return "%s.%s(%s)" % (
            self.__module__, self.__class__.__name__, args)

    def _update(self, **attrs):
        """Given attributes, update them on this instance

        This is intended to be used from within the proxy
        layer when updating instances that may have already
        been created.
        """
        body, header, uri = self._collect_attrs(attrs)

        self._body.update(body)
        self._header.update(header)
        self._uri.update(uri)

    def _collect_attrs(self, attrs):
        """Given attributes, return a dict per type of attribute

        This method splits up **attrs into separate dictionaries
        that correspond to the relevant body, header, and uri
        attributes that exist on this class.
        """
        body = self._consume_attrs(self._body_mapping(), attrs)
        header = self._consume_attrs(self._header_mapping(), attrs)
        uri = self._consume_attrs(self._uri_mapping(), attrs)

        return body, header, uri

    def _consume_attrs(self, mapping, attrs):
        """Given a mapping and attributes, return relevant matches

        This method finds keys in attrs that exist in the mapping, then
        both transposes them to their server-side equivalent key name
        to be returned, and finally pops them out of attrs. This allows
        us to only calculate their place and existence in a particular
        type of Resource component one time, rather than looking at the
        same source dict several times.
        """
        relevant_attrs = {}
        consumed_keys = []
        for key in attrs:
            if key in mapping:
                # Convert client-side key names into server-side.
                relevant_attrs[mapping[key]] = attrs[key]
                consumed_keys.append(key)
            elif key in mapping.values():
                # Server-side names can be stored directly.
                relevant_attrs[key] = attrs[key]
                consumed_keys.append(key)

        for key in consumed_keys:
            attrs.pop(key)

        return relevant_attrs

    @classmethod
    def _get_mapping(cls, component):
        """Return a dict of attributes of a given component on the class"""
        mapping = {}
        # Since we're looking at class definitions we need to include
        # subclasses, so check the whole MRO.
        for klass in cls.__mro__:
            for key, value in klass.__dict__.items():
                if isinstance(value, component):
                    # Make sure base classes don't end up overwriting
                    # mappings we've found previously in subclasses.
                    if key not in mapping:
                        mapping[key] = value.name
        return mapping

    @classmethod
    def _body_mapping(cls):
        """Return all Body members of this class"""
        return cls._get_mapping(Body)

    @classmethod
    def _header_mapping(cls):
        """Return all Header members of this class"""
        return cls._get_mapping(Header)

    @classmethod
    def _uri_mapping(cls):
        """Return all URI members of this class"""
        return cls._get_mapping(URI)

    @classmethod
    def _alternate_id(cls):
        """Return the name of any value known as an alternate_id

        NOTE: This will only ever return the first such alternate_id.
        Only one alternate_id should be specified.

        Returns an empty string if no name exists, as this method is
        consumed by _get_id and passed to getattr.
        """
        for key, value in cls.__dict__.items():
            if isinstance(value, Body):
                if value.alternate_id:
                    return key
        return ""

    @staticmethod
    def _get_id(value):
        """If a value is a Resource, return the canonical ID

        This will return either the value specified by `id` or
        `alternate_id` in that order if `value` is a Resource.
        If `value` is anything other than a Resource, likely to
        be a string already representing an ID, it is returned.
        """
        if isinstance(value, Resource):
            # Don't check _alternate_id unless we need to. It's an uncommon
            # case and it involves looping through the class' dict.
            id = value.id or getattr(value, value._alternate_id(), None)
            return id
        else:
            return value

    @classmethod
    def new(cls, **kwargs):
        """Create a new instance of this resource.

        Internally set flags such that it is marked as not present on the
        server.

        :param dict kwargs: Each of the named arguments will be set as
                            attributes on the resulting Resource object.
        """
        return cls(synchronized=False, **kwargs)

    @classmethod
    def existing(cls, **kwargs):
        """Create an instance of an existing remote resource.

        It is marked as an exact replication of a resource present on a server.

        :param dict kwargs: Each of the named arguments will be set as
                            attributes on the resulting Resource object.
        """
        return cls(synchronized=True, **kwargs)

    def _prepare_request(self, requires_id=True, prepend_key=False):
        """Prepare a request to be sent to the server

        Create operations don't require an ID, but all others do,
        so only try to append an ID when it's needed with
        requires_id. Create and update operations sometimes require
        their bodies to be contained within an dict -- if the
        instance contains a resource_key and prepend_key=True,
        the body will be wrapped in a dict with that key.

        Return a _Request object that contains the constructed URI
        as well a body and headers that are ready to send.
        Only dirty body and header contents will be returned.
        """
        body = self._body.dirty
        if prepend_key and self.resource_key is not None:
            body = {self.resource_key: body}

        headers = self._header.dirty

        uri = self.base_path % self._uri.attributes
        if requires_id:
            id = self._get_id(self)
            if id is None:
                raise exceptions.InvalidRequest(
                    "Request requires an ID but none was found")

            uri = utils.urljoin(uri, id)

        return _Request(uri, body, headers)

    def _transpose_component(self, component, mapping):
        """Transpose the keys in component based on a mapping

        This method converts a dict of server-side data to have
        the appropriate keys for attributes on this instance.
        """
        result = {}
        for key, value in mapping.items():
            if value in component:
                result[key] = component[value]

        return result

    def _translate_response(self, response, has_body=True):
        """Given a KSA response, inflate this instance with its data

        DELETE operations don't return a body, so only try to work
        with a body when has_body is True.

        This method updates attributes that correspond to headers
        and body on this instance and clears the dirty set.
        """
        if has_body:
            body = response.json()
            if self.resource_key and self.resource_key in body:
                body = body[self.resource_key]

            body = self._transpose_component(body, self._body_mapping())
            self._body.attributes.update(body)
            self._body.clean()

        headers = self._transpose_component(response.headers,
                                            self._header_mapping())
        self._header.attributes.update(headers)
        self._header.clean()

    def create(self, session):
        """Create a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_create` is not set to ``True``.
        """
        if not self.allow_create:
            raise exceptions.MethodNotSupported(self, "create")

        if self.id is None:
            request = self._prepare_request(requires_id=False,
                                            prepend_key=True)
            response = session.post(request.uri, endpoint_filter=self.service,
                                    json=request.body, headers=request.headers)
        else:
            request = self._prepare_request(requires_id=True,
                                            prepend_key=True)
            response = session.put(request.uri, endpoint_filter=self.service,
                                   json=request.body, headers=request.headers)

        self._translate_response(response)
        return self

    def get(self, session):
        """Get a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_get` is not set to ``True``.
        """
        if not self.allow_get:
            raise exceptions.MethodNotSupported(self, "get")

        request = self._prepare_request()

        response = session.get(request.uri, endpoint_filter=self.service)

        self._translate_response(response)
        return self

    def head(self, session):
        """Get headers from a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_head` is not set to ``True``.
        """
        if not self.allow_head:
            raise exceptions.MethodNotSupported(self, "head")

        request = self._prepare_request()

        response = session.head(request.uri, endpoint_filter=self.service,
                                headers={"Accept": ""})

        self._translate_response(response)
        return self

    def update(self, session):
        """Update the remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_update` is not set to ``True``.
        """
        # Only try to update if we actually have anything to update.
        if not any([self._body.dirty, self._header.dirty]):
            return self

        if not self.allow_update:
            raise exceptions.MethodNotSupported(self, "update")

        request = self._prepare_request(prepend_key=True)

        if self.patch_update:
            response = session.patch(request.uri, endpoint_filter=self.service,
                                     json=request.body,
                                     headers=request.headers)
        else:
            response = session.put(request.uri, endpoint_filter=self.service,
                                   json=request.body, headers=request.headers)

        self._translate_response(response)
        return self

    def delete(self, session):
        """Delete the remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_update` is not set to ``True``.
        """
        if not self.allow_delete:
            raise exceptions.MethodNotSupported(self, "delete")

        request = self._prepare_request()

        response = session.delete(request.uri, endpoint_filter=self.service,
                                  headers={"Accept": ""})

        self._translate_response(response, has_body=False)
        return self

    @classmethod
    def list(cls, session, paginated=False, **params):
        """This method is a generator which yields resource objects.

        This resource object list generator handles pagination and takes query
        params for response filtering.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param bool paginated: ``True`` if a GET to this resource returns
                               a paginated series of responses, or ``False``
                               if a GET returns only one page of data.
                               **When paginated is False only one
                               page of data will be returned regardless
                               of the API's support of pagination.**
        :param dict params: These keyword arguments are passed through the
            :meth:`~openstack.resource2.QueryParamter._transpose` method
            to find if any of them match expected query parameters to be
            sent in the *params* argument to
            :meth:`~openstack.session.Session.get`. They are additionally
            checked against the
            :data:`~openstack.resource2.Resource.base_path` format string
            to see if any path fragments need to be filled in by the contents
            of this argument.

        :return: A generator of :class:`Resource` objects.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_list` is not set to ``True``.
        """
        if not cls.allow_list:
            raise exceptions.MethodNotSupported(cls, "list")

        more_data = True
        query_params = cls._query_mapping._transpose(params)
        uri = cls.base_path % params

        while more_data:
            resp = session.get(uri, endpoint_filter=cls.service,
                               headers={"Accept": "application/json"},
                               params=query_params)
            resp = resp.json()
            if cls.resources_key:
                resp = resp[cls.resources_key]

            if not resp:
                more_data = False

            # Keep track of how many items we've yielded. If we yielded
            # less than our limit, we don't need to do an extra request
            # to get back an empty data set, which acts as a sentinel.
            yielded = 0
            new_marker = None
            for data in resp:
                value = cls.existing(**data)
                new_marker = value.id
                yielded += 1
                yield value

            if not paginated:
                return
            if "limit" in query_params and yielded < query_params["limit"]:
                return
            query_params["limit"] = yielded
            query_params["marker"] = new_marker

    @classmethod
    def _get_one_match(cls, name_or_id, results):
        """Given a list of results, return the match"""
        the_result = None
        for maybe_result in results:
            id_value = cls._get_id(maybe_result)
            name_value = maybe_result.name

            if (id_value == name_or_id) or (name_value == name_or_id):
                # Only allow one resource to be found. If we already
                # found a match, raise an exception to show it.
                if the_result is None:
                    the_result = maybe_result
                else:
                    msg = "More than one %s exists with the name '%s'."
                    msg = (msg % (cls.__name__, name_or_id))
                    raise exceptions.DuplicateResource(msg)

        return the_result

    @classmethod
    def find(cls, session, name_or_id, ignore_missing=True, **params):
        """Find a resource by its name or id.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param name_or_id: This resource's identifier, if needed by
                           the request. The default is ``None``.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict params: Any additional parameters to be passed into
                            underlying methods, such as to
                            :meth:`~openstack.resource2.Resource.existing`
                            in order to pass on URI parameters.

        :return: The :class:`Resource` object matching the given name or id
                 or None if nothing matches.
        :raises: :class:`openstack.exceptions.DuplicateResource` if more
                 than one resource is found for this request.
        :raises: :class:`openstack.exceptions.ResourceNotFound` if nothing
                 is found and ignore_missing is ``False``.
        """
        # Try to short-circuit by looking directly for a matching ID.
        try:
            match = cls.existing(id=name_or_id, **params)
            return match.get(session)
        except exceptions.NotFoundException:
            pass

        data = cls.list(session, **params)

        result = cls._get_one_match(name_or_id, data)
        if result is not None:
            return result

        if ignore_missing:
            return None
        raise exceptions.ResourceNotFound(
            "No %s found for %s" % (cls.__name__, name_or_id))


def wait_for_status(session, resource, status, failures, interval, wait):
    """Wait for the resource to be in a particular status.

    :param session: The session to use for making this request.
    :type session: :class:`~openstack.session.Session`
    :param resource: The resource to wait on to reach the status. The resource
                     must have a status attribute.
    :type resource: :class:`~openstack.resource.Resource`
    :param status: Desired status of the resource.
    :param list failures: Statuses that would indicate the transition
                          failed such as 'ERROR'.
    :param interval: Number of seconds to wait between checks.
    :param wait: Maximum number of seconds to wait for transition.

    :return: Method returns self on success.
    :raises: :class:`~openstack.exceptions.ResourceTimeout` transition
             to status failed to occur in wait seconds.
    :raises: :class:`~openstack.exceptions.ResourceFailure` resource
             transitioned to one of the failure states.
    :raises: :class:`~AttributeError` if the resource does not have a status
             attribute
    """
    if resource.status == status:
        return resource

    total_sleep = 0
    if failures is None:
        failures = []

    while total_sleep < wait:
        resource.get(session)
        if resource.status == status:
            return resource
        if resource.status in failures:
            msg = ("Resource %s transitioned to failure state %s" %
                   (resource.id, resource.status))
            raise exceptions.ResourceFailure(msg)
        time.sleep(interval)
        total_sleep += interval
    msg = "Timeout waiting for %s to transition to %s" % (resource.id, status)
    raise exceptions.ResourceTimeout(msg)


def wait_for_delete(session, resource, interval, wait):
    """Wait for the resource to be deleted.

    :param session: The session to use for making this request.
    :type session: :class:`~openstack.session.Session`
    :param resource: The resource to wait on to be deleted.
    :type resource: :class:`~openstack.resource.Resource`
    :param interval: Number of seconds to wait between checks.
    :param wait: Maximum number of seconds to wait for the delete.

    :return: Method returns self on success.
    :raises: :class:`~openstack.exceptions.ResourceTimeout` transition
             to status failed to occur in wait seconds.
    """
    total_sleep = 0
    while total_sleep < wait:
        try:
            resource.get(session)
        except exceptions.NotFoundException:
            return resource
        time.sleep(interval)
        total_sleep += interval
    msg = "Timeout waiting for %s delete" % (resource.id)
    raise exceptions.ResourceTimeout(msg)
