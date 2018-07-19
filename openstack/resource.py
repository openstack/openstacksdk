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
are of a component type, including :class:`~openstack.resource.Body`,
:class:`~openstack.resource.Header`, and :class:`~openstack.resource.URI`.

For update management, :class:`~openstack.resource.Resource` employs
a series of :class:`~openstack.resource._ComponentManager` instances
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

from keystoneauth1 import adapter
import munch
from requests import structures

from openstack import _log
from openstack import exceptions
from openstack import format
from openstack import utils


def _convert_type(value, data_type, list_type=None):
    # This should allow handling list of dicts that have their own
    # Component type directly. See openstack/compute/v2/limits.py
    # and the RateLimit type for an example.
    if not data_type:
        return value
    if issubclass(data_type, list):
        if isinstance(value, (list, tuple, set)):
            if not list_type:
                return value
            ret = []
            for raw in value:
                ret.append(_convert_type(raw, list_type))
            return ret
        elif list_type:
            return [_convert_type(value, list_type)]
        # "if-match" in Object is a good example of the need here
        return [value]
    elif isinstance(value, data_type):
        return value
    if not isinstance(value, data_type):
        if issubclass(data_type, format.Formatter):
            return data_type.deserialize(value)
        # This should allow handling sub-dicts that have their own
        # Component type directly. See openstack/compute/v2/limits.py
        # and the AbsoluteLimits type for an example.
        if isinstance(value, dict):
            return data_type(**value)
        return data_type(value)


class _BaseComponent(object):

    # The name this component is being tracked as in the Resource
    key = None
    # The class to be used for mappings
    _map_cls = dict

    def __init__(self, name, type=None, default=None, alias=None,
                 alternate_id=False, list_type=None, **kwargs):
        """A typed descriptor for a component that makes up a Resource

        :param name: The name this component exists as on the server
        :param type: The type this component is expected to be by the server.
                     By default this is None, meaning any value you specify
                     will work. If you specify type=dict and then set a
                     component to a string, __set__ will fail, for example.
        :param default: Typically None, but any other default can be set.
        :param alias: If set, alternative attribute on object to return.
        :param alternate_id: When `True`, this property is known
                             internally as a value that can be sent
                             with requests that require an ID but
                             when `id` is not a name the Resource has.
                             This is a relatively uncommon case, and this
                             setting should only be used once per Resource.
        :param list_type: If type is `list`, list_type designates what the
                          type of the elements of the list should be.
        """
        self.name = name
        self.type = type
        self.default = default
        self.alias = alias
        self.alternate_id = alternate_id
        self.list_type = list_type

    def __get__(self, instance, owner):
        if instance is None:
            return None

        attributes = getattr(instance, self.key)

        try:
            value = attributes[self.name]
        except KeyError:
            if self.alias:
                return getattr(instance, self.alias)
            return self.default

        # self.type() should not be called on None objects.
        if value is None:
            return None

        return _convert_type(value, self.type, self.list_type)

    def __set__(self, instance, value):
        if value != self.default:
            value = _convert_type(value, self.type, self.list_type)

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
    _map_cls = structures.CaseInsensitiveDict


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

    def __init__(self, url, body, headers):
        self.url = url
        self.body = body
        self.headers = headers


class QueryParameters(object):

    def __init__(self, *names, **mappings):
        """Create a dict of accepted query parameters

        :param names: List of strings containing client-side query parameter
                      names. Each name in the list maps directly to the name
                      expected by the server.

        :param mappings: Key-value pairs where the key is the client-side
                         name we'll accept here and the value is the name
                         the server expects, e.g, changes_since=changes-since

        By default, both limit and marker are included in the initial mapping
        as they're the most common query parameters used for listing resources.
        """
        self._mapping = {"limit": "limit", "marker": "marker"}
        self._mapping.update(dict({name: name for name in names}, **mappings))

    def _validate(self, query, base_path=None):
        """Check that supplied query keys match known query mappings

        :param dict query: Collection of key-value pairs where each key is the
                           client-side parameter name or server side name.
        :param base_path: Formatted python string of the base url path for
                          the resource.
        """
        expected_params = list(self._mapping.keys())
        expected_params += self._mapping.values()

        if base_path:
            expected_params += utils.get_string_format_keys(base_path)

        invalid_keys = set(query.keys()) - set(expected_params)
        if invalid_keys:
            raise exceptions.InvalidResourceQuery(
                message="Invalid query params: %s" % ",".join(invalid_keys),
                extra_data=invalid_keys)

    def _transpose(self, query):
        """Transpose the keys in query based on the mapping

        If a query is supplied with its server side name, we will still use
        it, but take preference to the client-side name when both are supplied.

        :param dict query: Collection of key-value pairs where each key is the
                           client-side parameter name to be transposed to its
                           server side name.
        """
        result = {}
        for key, value in self._mapping.items():
            if key in query:
                result[value] = query[key]
            elif value in query:
                result[value] = query[value]
        return result


class Resource(object):

    #: Singular form of key for resource.
    resource_key = None
    #: Plural form of key for resource.
    resources_key = None
    #: Key used for pagination links
    pagination_key = None

    #: The ID of this resource.
    id = Body("id")
    #: The name of this resource.
    name = Body("name")
    #: The location of this resource.
    location = Header("Location")

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

    #: Method for udating a resource (PUT, PATCH, POST)
    update_method = "PUT"
    #: Method for creating a resource (POST, PUT)
    create_method = "POST"

    #: Do calls for this resource require an id
    requires_id = True
    #: Do responses for this resource have bodies
    has_body = True
    #: Is this a detailed version of another Resource
    detail_for = None

    def __init__(self, _synchronized=False, **attrs):
        """The base resource

        :param bool _synchronized: This is not intended to be used directly.
                    See :meth:`~openstack.resource.Resource.new` and
                    :meth:`~openstack.resource.Resource.existing`.
        """

        # NOTE: _collect_attrs modifies **attrs in place, removing
        # items as they match up with any of the body, header,
        # or uri mappings.
        body, header, uri = self._collect_attrs(attrs)
        # TODO(briancurtin): at this point if attrs has anything left
        # they're not being set anywhere. Log this? Raise exception?
        # How strict should we be here? Should strict be an option?

        self._body = _ComponentManager(attributes=body,
                                       synchronized=_synchronized)
        self._header = _ComponentManager(attributes=header,
                                         synchronized=_synchronized)
        self._uri = _ComponentManager(attributes=uri,
                                      synchronized=_synchronized)

    def __repr__(self):
        pairs = ["%s=%s" % (k, v) for k, v in dict(itertools.chain(
            self._body.attributes.items(),
            self._header.attributes.items(),
            self._uri.attributes.items())).items()]
        args = ", ".join(pairs)

        return "%s.%s(%s)" % (
            self.__module__, self.__class__.__name__, args)

    def __eq__(self, comparand):
        """Return True if another resource has the same contents"""
        if not isinstance(comparand, Resource):
            return False
        return all([self._body.attributes == comparand._body.attributes,
                    self._header.attributes == comparand._header.attributes,
                    self._uri.attributes == comparand._uri.attributes])

    def __getattribute__(self, name):
        """Return an attribute on this instance

        This is mostly a pass-through except for a specialization on
        the 'id' name, as this can exist under a different name via the
        `alternate_id` argument to resource.Body.
        """
        if name == "id":
            if name in self._body:
                return self._body[name]
            else:
                try:
                    return self._body[self._alternate_id()]
                except KeyError:
                    return None
        else:
            return object.__getattribute__(self, name)

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
        body = self._consume_body_attrs(attrs)
        header = self._consume_header_attrs(attrs)
        uri = self._consume_uri_attrs(attrs)

        return body, header, uri

    def _consume_body_attrs(self, attrs):
        return self._consume_mapped_attrs(Body, attrs)

    def _consume_header_attrs(self, attrs):
        return self._consume_mapped_attrs(Header, attrs)

    def _consume_uri_attrs(self, attrs):
        return self._consume_mapped_attrs(URI, attrs)

    def _update_from_body_attrs(self, attrs):
        body = self._consume_body_attrs(attrs)
        self._body.attributes.update(body)
        self._body.clean()

    def _update_from_header_attrs(self, attrs):
        headers = self._consume_header_attrs(attrs)
        self._header.attributes.update(headers)
        self._header.clean()

    def _update_uri_from_attrs(self, attrs):
        uri = self._consume_uri_attrs(attrs)
        self._uri.attributes.update(uri)
        self._uri.clean()

    def _consume_mapped_attrs(self, mapping_cls, attrs):
        mapping = self._get_mapping(mapping_cls)
        return self._consume_attrs(mapping, attrs)

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
        for key, value in attrs.items():
            # We want the key lookup in mapping to be case insensitive if the
            # mapping is, thus the use of get. We want value to be exact.
            # If we find a match, we then have to loop over the mapping for
            # to find the key to return, as there isn't really a "get me the
            # key that matches this other key". We lower() in the inner loop
            # because we've already done case matching in the outer loop.
            if key in mapping.values() or mapping.get(key):
                for map_key, map_value in mapping.items():
                    if key.lower() in (map_key.lower(), map_value.lower()):
                        relevant_attrs[map_key] = value
                        consumed_keys.append(key)
                continue

        for key in consumed_keys:
            attrs.pop(key)

        return relevant_attrs

    @classmethod
    def _get_mapping(cls, component):
        """Return a dict of attributes of a given component on the class"""
        mapping = component._map_cls()
        ret = component._map_cls()
        # Since we're looking at class definitions we need to include
        # subclasses, so check the whole MRO.
        for klass in cls.__mro__:
            for key, value in klass.__dict__.items():
                if isinstance(value, component):
                    # Make sure base classes don't end up overwriting
                    # mappings we've found previously in subclasses.
                    if key not in mapping:
                        # Make it this way first, to get MRO stuff correct.
                        mapping[key] = value.name
        for k, v in mapping.items():
            ret[v] = k
        return ret

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
        for value in cls.__dict__.values():
            if isinstance(value, Body):
                if value.alternate_id:
                    return value.name
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
            return value.id
        else:
            return value

    @classmethod
    def new(cls, **kwargs):
        """Create a new instance of this resource.

        When creating the instance set the ``_synchronized`` parameter
        of :class:`Resource` to ``False`` to indicate that the resource does
        not yet exist on the server side. This marks all attributes passed
        in ``**kwargs`` as "dirty" on the resource, and thusly tracked
        as necessary in subsequent calls such as :meth:`update`.

        :param dict kwargs: Each of the named arguments will be set as
                            attributes on the resulting Resource object.
        """
        return cls(_synchronized=False, **kwargs)

    @classmethod
    def existing(cls, **kwargs):
        """Create an instance of an existing remote resource.

        When creating the instance set the ``_synchronized`` parameter
        of :class:`Resource` to ``True`` to indicate that it represents the
        state of an existing server-side resource. As such, all attributes
        passed in ``**kwargs`` are considered "clean", such that an immediate
        :meth:`update` call would not generate a body of attributes to be
        modified on the server.

        :param dict kwargs: Each of the named arguments will be set as
                            attributes on the resulting Resource object.
        """
        return cls(_synchronized=True, **kwargs)

    @classmethod
    def _from_munch(cls, obj, synchronized=True):
        """Create an instance from a ``munch.Munch`` object.

        This is intended as a temporary measure to convert between shade-style
        Munch objects and original openstacksdk resources.

        :param obj: a ``munch.Munch`` object to convert from.
        :param bool synchronized: whether this object already exists on server
            Must be set to ``False`` for newly created objects.
        """
        return cls(_synchronized=synchronized, **obj)

    def to_dict(self, body=True, headers=True, ignore_none=False,
                original_names=False):
        """Return a dictionary of this resource's contents

        :param bool body: Include the :class:`~openstack.resource.Body`
                          attributes in the returned dictionary.
        :param bool headers: Include the :class:`~openstack.resource.Header`
                             attributes in the returned dictionary.
        :param bool ignore_none: When True, exclude key/value pairs where
                                 the value is None. This will exclude
                                 attributes that the server hasn't returned.
        :param bool original_names: When True, use attribute names as they
                                    were received from the server.

        :return: A dictionary of key/value pairs where keys are named
                 as they exist as attributes of this class.
        """
        mapping = {}

        components = []
        if body:
            components.append(Body)
        if headers:
            components.append(Header)
        if not components:
            raise ValueError(
                "At least one of `body` or `headers` must be True")

        # isinstance stricly requires this to be a tuple
        components = tuple(components)

        # NOTE: This is similar to the implementation in _get_mapping
        # but is slightly different in that we're looking at an instance
        # and we're mapping names on this class to their actual stored
        # values.
        # Since we're looking at class definitions we need to include
        # subclasses, so check the whole MRO.
        for klass in self.__class__.__mro__:
            for attr, component in klass.__dict__.items():
                if isinstance(component, components):
                    if original_names:
                        key = component.name
                    else:
                        key = attr
                    # Make sure base classes don't end up overwriting
                    # mappings we've found previously in subclasses.
                    if key not in mapping:
                        value = getattr(self, attr, None)
                        if ignore_none and value is None:
                            continue
                        if isinstance(value, Resource):
                            mapping[key] = value.to_dict()
                        elif (value and isinstance(value, list)
                              and isinstance(value[0], Resource)):
                            converted = []
                            for raw in value:
                                converted.append(raw.to_dict())
                            mapping[key] = converted
                        else:
                            mapping[key] = value

        return mapping

    def _to_munch(self):
        """Convert this resource into a Munch compatible with shade."""
        return munch.Munch(self.to_dict(body=True, headers=False,
                                        original_names=True))

    def _prepare_request(self, requires_id=None, prepend_key=False):
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
        if requires_id is None:
            requires_id = self.requires_id

        body = self._body.dirty
        if prepend_key and self.resource_key is not None:
            body = {self.resource_key: body}

        # TODO(mordred) Ensure headers have string values better than this
        headers = {}
        for k, v in self._header.dirty.items():
            if isinstance(v, list):
                headers[k] = ", ".join(v)
            else:
                headers[k] = str(v)

        uri = self.base_path % self._uri.attributes
        if requires_id:
            if self.id is None:
                raise exceptions.InvalidRequest(
                    "Request requires an ID but none was found")

            uri = utils.urljoin(uri, self.id)

        return _Request(uri, body, headers)

    def _translate_response(self, response, has_body=None, error_message=None):
        """Given a KSA response, inflate this instance with its data

        DELETE operations don't return a body, so only try to work
        with a body when has_body is True.

        This method updates attributes that correspond to headers
        and body on this instance and clears the dirty set.
        """
        if has_body is None:
            has_body = self.has_body
        exceptions.raise_from_response(response, error_message=error_message)
        if has_body:
            body = response.json()
            if self.resource_key and self.resource_key in body:
                body = body[self.resource_key]

            body = self._consume_body_attrs(body)
            self._body.attributes.update(body)
            self._body.clean()

        headers = self._consume_header_attrs(response.headers)
        self._header.attributes.update(headers)
        self._header.clean()

    @classmethod
    def _get_session(cls, session):
        """Attempt to get an Adapter from a raw session.

        Some older code used conn.session has the session argument to Resource
        methods. That does not work anymore, as Resource methods expect an
        Adapter not a session. We've hidden an _sdk_connection on the Session
        stored on the connection. If we get something that isn't an Adapter,
        pull the connection from the Session and look up the adapter by
        service_type.
        """
        # TODO(mordred) We'll need to do this for every method in every
        # Resource class that is calling session.$something to be complete.
        if isinstance(session, adapter.Adapter):
            return session
        if hasattr(session, '_sdk_connection'):
            service_type = cls.service['service_type']
            return getattr(session._sdk_connection, service_type)
        raise ValueError(
            "The session argument to Resource methods requires either an"
            " instance of an openstack.proxy.Proxy object or at the very least"
            " a raw keystoneauth1.adapter.Adapter.")

    def create(self, session, prepend_key=True):
        """Create a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param prepend_key: A boolean indicating whether the resource_key
                            should be prepended in a resource creation
                            request. Default to True.

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_create` is not set to ``True``.
        """
        if not self.allow_create:
            raise exceptions.MethodNotSupported(self, "create")

        session = self._get_session(session)
        if self.create_method == 'PUT':
            request = self._prepare_request(requires_id=True,
                                            prepend_key=prepend_key)
            response = session.put(request.url,
                                   json=request.body, headers=request.headers)
        elif self.create_method == 'POST':
            request = self._prepare_request(requires_id=False,
                                            prepend_key=prepend_key)
            response = session.post(request.url,
                                    json=request.body, headers=request.headers)
        else:
            raise exceptions.ResourceFailure(
                msg="Invalid create method: %s" % self.create_method)

        self._translate_response(response)
        return self

    def get(self, session, requires_id=True, error_message=None):
        """Get a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param boolean requires_id: A boolean indicating whether resource ID
                                    should be part of the requested URI.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_get` is not set to ``True``.
        """
        if not self.allow_get:
            raise exceptions.MethodNotSupported(self, "get")

        request = self._prepare_request(requires_id=requires_id)
        session = self._get_session(session)
        response = session.get(request.url)
        kwargs = {}
        if error_message:
            kwargs['error_message'] = error_message

        self._translate_response(response, **kwargs)
        return self

    def head(self, session):
        """Get headers from a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_head` is not set to ``True``.
        """
        if not self.allow_head:
            raise exceptions.MethodNotSupported(self, "head")

        request = self._prepare_request()

        session = self._get_session(session)
        response = session.head(request.url,
                                headers={"Accept": ""})

        self._translate_response(response, has_body=False)
        return self

    def update(self, session, prepend_key=True, has_body=True):
        """Update the remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param prepend_key: A boolean indicating whether the resource_key
                            should be prepended in a resource update request.
                            Default to True.

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_update` is not set to ``True``.
        """
        # The id cannot be dirty for an update
        self._body._dirty.discard("id")

        # Only try to update if we actually have anything to update.
        if not any([self._body.dirty, self._header.dirty]):
            return self

        if not self.allow_update:
            raise exceptions.MethodNotSupported(self, "update")

        request = self._prepare_request(prepend_key=prepend_key)
        session = self._get_session(session)

        if self.update_method == 'PATCH':
            response = session.patch(
                request.url, json=request.body, headers=request.headers)
        elif self.update_method == 'POST':
            response = session.post(
                request.url, json=request.body, headers=request.headers)
        elif self.update_method == 'PUT':
            response = session.put(
                request.url, json=request.body, headers=request.headers)
        else:
            raise exceptions.ResourceFailure(
                msg="Invalid update method: %s" % self.update_method)

        self._translate_response(response, has_body=has_body)
        return self

    def delete(self, session, error_message=None):
        """Delete the remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_update` is not set to ``True``.
        """
        if not self.allow_delete:
            raise exceptions.MethodNotSupported(self, "delete")

        request = self._prepare_request()
        session = self._get_session(session)

        response = session.delete(request.url,
                                  headers={"Accept": ""})
        kwargs = {}
        if error_message:
            kwargs['error_message'] = error_message

        self._translate_response(response, has_body=False, **kwargs)
        return self

    @classmethod
    def list(cls, session, paginated=False, **params):
        """This method is a generator which yields resource objects.

        This resource object list generator handles pagination and takes query
        params for response filtering.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param bool paginated: ``True`` if a GET to this resource returns
                               a paginated series of responses, or ``False``
                               if a GET returns only one page of data.
                               **When paginated is False only one
                               page of data will be returned regardless
                               of the API's support of pagination.**
        :param dict params: These keyword arguments are passed through the
            :meth:`~openstack.resource.QueryParamter._transpose` method
            to find if any of them match expected query parameters to be
            sent in the *params* argument to
            :meth:`~keystoneauth1.adapter.Adapter.get`. They are additionally
            checked against the
            :data:`~openstack.resource.Resource.base_path` format string
            to see if any path fragments need to be filled in by the contents
            of this argument.

        :return: A generator of :class:`Resource` objects.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_list` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.InvalidResourceQuery` if query
                 contains invalid params.
        """
        if not cls.allow_list:
            raise exceptions.MethodNotSupported(cls, "list")
        session = cls._get_session(session)

        cls._query_mapping._validate(params, base_path=cls.base_path)
        query_params = cls._query_mapping._transpose(params)
        uri = cls.base_path % params

        limit = query_params.get('limit')

        # Track the total number of resources yielded so we can paginate
        # swift objects
        total_yielded = 0
        while uri:
            # Copy query_params due to weird mock unittest interactions
            response = session.get(
                uri,
                headers={"Accept": "application/json"},
                params=query_params.copy())
            exceptions.raise_from_response(response)
            data = response.json()

            # Discard any existing pagination keys
            query_params.pop('marker', None)
            query_params.pop('limit', None)

            if cls.resources_key:
                resources = data[cls.resources_key]
            else:
                resources = data

            if not isinstance(resources, list):
                resources = [resources]

            marker = None
            for raw_resource in resources:
                # Do not allow keys called "self" through. Glance chose
                # to name a key "self", so we need to pop it out because
                # we can't send it through cls.existing and into the
                # Resource initializer. "self" is already the first
                # argument and is practically a reserved word.
                raw_resource.pop("self", None)

                value = cls.existing(**raw_resource)
                marker = value.id
                yield value
                total_yielded += 1

            if resources and paginated:
                uri, next_params = cls._get_next_link(
                    uri, response, data, marker, limit, total_yielded)
                query_params.update(next_params)
            else:
                return

    @classmethod
    def _get_next_link(cls, uri, response, data, marker, limit, total_yielded):
        next_link = None
        params = {}
        if isinstance(data, dict):
            pagination_key = cls.pagination_key

            if not pagination_key and 'links' in data:
                # api-wg guidelines are for a links dict in the main body
                pagination_key == 'links'
            if not pagination_key and cls.resources_key:
                # Nova has a {key}_links dict in the main body
                pagination_key = '{key}_links'.format(key=cls.resources_key)
            if pagination_key:
                links = data.get(pagination_key, {})
                for item in links:
                    if item.get('rel') == 'next' and 'href' in item:
                        next_link = item['href']
                        break
            # Glance has a next field in the main body
            next_link = next_link or data.get('next')
            if next_link and next_link.startswith('/v'):
                next_link = next_link[next_link.find('/', 1) + 1:]

        if not next_link and 'next' in response.links:
            # RFC5988 specifies Link headers and requests parses them if they
            # are there. We prefer link dicts in resource body, but if those
            # aren't there and Link headers are, use them.
            next_link = response.links['next']['uri']
        # Swift provides a count of resources in a header and a list body
        if not next_link and cls.pagination_key:
            total_count = response.headers.get(cls.pagination_key)
            if total_count:
                total_count = int(total_count)
                if total_count > total_yielded:
                    params['marker'] = marker
                    if limit:
                        params['limit'] = limit
                    next_link = uri
        # If we still have no link, and limit was given and is non-zero,
        # and the number of records yielded equals the limit, then the user
        # is playing pagination ball so we should go ahead and try once more.
        if not next_link and limit:
            next_link = uri
            params['marker'] = marker
            params['limit'] = limit
        return next_link, params

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
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param name_or_id: This resource's identifier, if needed by
                           the request. The default is ``None``.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :param dict params: Any additional parameters to be passed into
                            underlying methods, such as to
                            :meth:`~openstack.resource.Resource.existing`
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


def _normalize_status(status):
    if status is not None:
        status = status.lower()
    return status


def wait_for_status(session, resource, status, failures, interval=None,
                    wait=None, attribute='status'):
    """Wait for the resource to be in a particular status.

    :param session: The session to use for making this request.
    :type session: :class:`~keystoneauth1.adapter.Adapter`
    :param resource: The resource to wait on to reach the status. The resource
                     must have a status attribute specified via ``attribute``.
    :type resource: :class:`~openstack.resource.Resource`
    :param status: Desired status of the resource.
    :param list failures: Statuses that would indicate the transition
                          failed such as 'ERROR'. Defaults to ['ERROR'].
    :param interval: Number of seconds to wait between checks.
                     Set to ``None`` to use the default interval.
    :param wait: Maximum number of seconds to wait for transition.
                 Set to ``None`` to wait forever.
    :param attribute: Name of the resource attribute that contains the status.

    :return: The updated resource.
    :raises: :class:`~openstack.exceptions.ResourceTimeout` transition
             to status failed to occur in wait seconds.
    :raises: :class:`~openstack.exceptions.ResourceFailure` resource
             transitioned to one of the failure states.
    :raises: :class:`~AttributeError` if the resource does not have a status
             attribute
    """
    log = _log.setup_logging(__name__)

    current_status = getattr(resource, attribute)
    if _normalize_status(current_status) == status.lower():
        return resource

    if failures is None:
        failures = ['ERROR']

    failures = [f.lower() for f in failures]
    name = "{res}:{id}".format(res=resource.__class__.__name__, id=resource.id)
    msg = "Timeout waiting for {name} to transition to {status}".format(
        name=name, status=status)

    for count in utils.iterate_timeout(
            timeout=wait,
            message=msg,
            wait=interval):
        resource = resource.get(session)

        if not resource:
            raise exceptions.ResourceFailure(
                "{name} went away while waiting for {status}".format(
                    name=name, status=status))

        new_status = getattr(resource, attribute)
        normalized_status = _normalize_status(new_status)
        if normalized_status == status.lower():
            return resource
        elif normalized_status in failures:
            raise exceptions.ResourceFailure(
                "{name} transitioned to failure state {status}".format(
                    name=name, status=new_status))

        log.debug('Still waiting for resource %s to reach state %s, '
                  'current state is %s', name, status, new_status)


def wait_for_delete(session, resource, interval, wait):
    """Wait for the resource to be deleted.

    :param session: The session to use for making this request.
    :type session: :class:`~keystoneauth1.adapter.Adapter`
    :param resource: The resource to wait on to be deleted.
    :type resource: :class:`~openstack.resource.Resource`
    :param interval: Number of seconds to wait between checks.
    :param wait: Maximum number of seconds to wait for the delete.

    :return: Method returns self on success.
    :raises: :class:`~openstack.exceptions.ResourceTimeout` transition
             to status failed to occur in wait seconds.
    """
    orig_resource = resource
    for count in utils.iterate_timeout(
            timeout=wait,
            message="Timeout waiting for {res}:{id} to delete".format(
                res=resource.__class__.__name__,
                id=resource.id),
            wait=interval):
        try:
            resource = resource.get(session)
            if not resource:
                return orig_resource
            if resource.status.lower() == 'deleted':
                return resource
        except exceptions.NotFoundException:
            return orig_resource
