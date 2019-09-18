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
import inspect
import itertools

import jsonpatch
import operator
from keystoneauth1 import adapter
from keystoneauth1 import discover
import munch
from requests import structures
import six

from openstack import _log
from openstack import exceptions
from openstack import format
from openstack import utils

_SEEN_FORMAT = '{name}_seen'


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

    def __init__(self, name, type=None, default=None, alias=None, aka=None,
                 alternate_id=False, list_type=None, coerce_to_default=False,
                 **kwargs):
        """A typed descriptor for a component that makes up a Resource

        :param name: The name this component exists as on the server
        :param type:
            The type this component is expected to be by the server.
            By default this is None, meaning any value you specify
            will work. If you specify type=dict and then set a
            component to a string, __set__ will fail, for example.
        :param default: Typically None, but any other default can be set.
        :param alias: If set, alternative attribute on object to return.
        :param aka: If set, additional name attribute would be available under.
        :param alternate_id:
            When `True`, this property is known internally as a value that
            can be sent with requests that require an ID but when `id` is
            not a name the Resource has. This is a relatively uncommon case,
            and this setting should only be used once per Resource.
        :param list_type:
            If type is `list`, list_type designates what the type of the
            elements of the list should be.
        :param coerce_to_default:
            If the Component is None or not present, force the given default
            to be used. If a default is not given but a type is given,
            construct an empty version of the type in question.
        """
        self.name = name
        self.type = type
        if type is not None and coerce_to_default and not default:
            self.default = type()
        else:
            self.default = default
        self.alias = alias
        self.aka = aka
        self.alternate_id = alternate_id
        self.list_type = list_type
        self.coerce_to_default = coerce_to_default

    def __get__(self, instance, owner):
        if instance is None:
            return self

        attributes = getattr(instance, self.key)

        try:
            value = attributes[self.name]
        except KeyError:
            if self.alias:
                # Resource attributes can be aliased to each other. If neither
                # of them exist, then simply doing a
                # getattr(instance, self.alias) here sends things into
                # infinite recursion (this _get method is what gets called
                # when getattr(instance) is called.
                # To combat that, we set a flag on the instance saying that
                # we have seen the current name, and we check before trying
                # to resolve the alias if there is already a flag set for that
                # alias name. We then remove the seen flag for ourselves after
                # we exit the alias getattr to clean up after ourselves for
                # the next time.
                alias_flag = _SEEN_FORMAT.format(name=self.alias)
                if not getattr(instance, alias_flag, False):
                    seen_flag = _SEEN_FORMAT.format(name=self.name)
                    # Prevent infinite recursion
                    setattr(instance, seen_flag, True)
                    value = getattr(instance, self.alias)
                    delattr(instance, seen_flag)
                    return value
            return self.default

        # self.type() should not be called on None objects.
        if value is None:
            return None

        return _convert_type(value, self.type, self.list_type)

    def __set__(self, instance, value):
        if self.coerce_to_default and value is None:
            value = self.default
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


class Computed(_BaseComponent):
    """Computed attributes"""

    key = "_computed"


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

    def clean(self, only=None):
        """Signal that the resource no longer has modified attributes.

        :param only: an optional set of attributes to no longer consider
            changed
        """
        if only:
            self._dirty = self._dirty - set(only)
        else:
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
                         the server expects, e.g, changes_since=changes-since.
                         Additionally, a value can be a dict with optional keys
                         name - server-side name,
                         type - callable to convert from client to server
                         representation.

        By default, both limit and marker are included in the initial mapping
        as they're the most common query parameters used for listing resources.
        """
        self._mapping = {"limit": "limit", "marker": "marker"}
        self._mapping.update({name: name for name in names})
        self._mapping.update(mappings)

    def _validate(self, query, base_path=None, allow_unknown_params=False):
        """Check that supplied query keys match known query mappings

        :param dict query: Collection of key-value pairs where each key is the
            client-side parameter name or server side name.
        :param base_path: Formatted python string of the base url path for
            the resource.
        : param allow_unknown_params: Exclude query params not known by the
            resource.

        :returns: Filtered collection of the supported QueryParameters
        """
        expected_params = list(self._mapping.keys())
        expected_params.extend(
            value.get('name', key) if isinstance(value, dict) else value
            for key, value in self._mapping.items())

        if base_path:
            expected_params += utils.get_string_format_keys(base_path)

        invalid_keys = set(query.keys()) - set(expected_params)
        if not invalid_keys:
            return query
        else:
            if not allow_unknown_params:
                raise exceptions.InvalidResourceQuery(
                    message="Invalid query params: %s" %
                    ",".join(invalid_keys),
                    extra_data=invalid_keys)
            else:
                known_keys = set(query.keys()).intersection(
                    set(expected_params))
                return {k: query[k] for k in known_keys}

    def _transpose(self, query, resource_type):
        """Transpose the keys in query based on the mapping

        If a query is supplied with its server side name, we will still use
        it, but take preference to the client-side name when both are supplied.

        :param dict query: Collection of key-value pairs where each key is the
                           client-side parameter name to be transposed to its
                           server side name.
        :param resource_type: Class of a resource.
        """
        result = {}
        for client_side, server_side in self._mapping.items():
            if isinstance(server_side, dict):
                name = server_side.get('name', client_side)
                type_ = server_side.get('type')
            else:
                name = server_side
                type_ = None

            # NOTE(dtantsur): a small hack to be compatible with both
            # single-argument (like int) and double-argument type functions.
            try:
                provide_resource_type = (
                    len(inspect.getargspec(type_).args) > 1)
            except TypeError:
                provide_resource_type = False

            if client_side in query:
                value = query[client_side]
            elif name in query:
                value = query[name]
            else:
                continue

            if type_ is not None:
                if provide_resource_type:
                    result[name] = type_(value, resource_type)
                else:
                    result[name] = type_(value)
            else:
                result[name] = value
        return result


class Resource(dict):
    # TODO(mordred) While this behaves mostly like a munch for the purposes
    # we need, sub-resources, such as Server.security_groups, which is a list
    # of dicts, will contain lists of real dicts, not lists of munch-like dict
    # objects. We should probably figure out a Resource class, perhaps
    # SubResource or something, that we can use to define the data-model of
    # complex object attributes where those attributes are not already covered
    # by a different resource such as Server.image which should ultimately
    # be an Image. We subclass dict so that things like json.dumps and pprint
    # will work properly.

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
    #: The OpenStack location of this resource.
    location = Computed('location')

    #: Mapping of accepted query parameter names.
    _query_mapping = QueryParameters()

    #: The base part of the URI for this resource.
    base_path = ""

    #: The service associated with this resource to find the service URL.
    service = None

    #: Allow create operation for this resource.
    allow_create = False
    #: Allow get operation for this resource.
    allow_fetch = False
    #: Allow update operation for this resource.
    allow_commit = False
    #: Allow delete operation for this resource.
    allow_delete = False
    #: Allow list operation for this resource.
    allow_list = False
    #: Allow head operation for this resource.
    allow_head = False
    #: Allow patch operation for this resource.
    allow_patch = False

    # TODO(mordred) Unused - here for transition with OSC. Remove once
    # OSC no longer checks for allow_get
    allow_get = True

    #: Commits happen without header or body being dirty.
    allow_empty_commit = False

    #: Method for committing a resource (PUT, PATCH, POST)
    commit_method = "PUT"
    #: Method for creating a resource (POST, PUT)
    create_method = "POST"
    #: Whether commit uses JSON patch format.
    commit_jsonpatch = False

    #: Do calls for this resource require an id
    requires_id = True
    #: Whether create requires an ID (determined from method if None).
    create_requires_id = None
    #: Do responses for this resource have bodies
    has_body = True
    #: Does create returns a body (if False requires ID), defaults to has_body
    create_returns_body = None

    #: Maximum microversion to use for getting/creating/updating the Resource
    _max_microversion = None
    #: API microversion (string or None) this Resource was loaded with
    microversion = None

    _connection = None
    _body = None
    _header = None
    _uri = None
    _computed = None
    _original_body = None
    _delete_response_class = None
    _store_unknown_attrs_as_properties = False

    # Placeholder for aliases as dict of {__alias__:__original}
    _attr_aliases = {}

    def __init__(self, _synchronized=False, connection=None, **attrs):
        """The base resource

        :param bool _synchronized:
            This is not intended to be used directly. See
            :meth:`~openstack.resource.Resource.new` and
            :meth:`~openstack.resource.Resource.existing`.
        :param openstack.connection.Connection connection:
            Reference to the Connection being used. Defaults to None to allow
            Resource objects to be used without an active Connection, such as
            in unit tests. Use of ``self._connection`` in Resource code should
            protect itself with a check for None.
        """
        self._connection = connection
        self.microversion = attrs.pop('microversion', None)
        # NOTE: _collect_attrs modifies **attrs in place, removing
        # items as they match up with any of the body, header,
        # or uri mappings.
        body, header, uri, computed = self._collect_attrs(attrs)

        self._body = _ComponentManager(
            attributes=body,
            synchronized=_synchronized)
        self._header = _ComponentManager(
            attributes=header,
            synchronized=_synchronized)
        self._uri = _ComponentManager(
            attributes=uri,
            synchronized=_synchronized)
        self._computed = _ComponentManager(
            attributes=computed,
            synchronized=_synchronized)
        if self.commit_jsonpatch or self.allow_patch:
            # We need the original body to compare against
            if _synchronized:
                self._original_body = self._body.attributes.copy()
            elif self.id:
                # Never record ID as dirty.
                self._original_body = {
                    self._alternate_id() or 'id': self.id
                }
            else:
                self._original_body = {}
        if self._store_unknown_attrs_as_properties:
            # When storing of unknown attributes is requested - ensure
            # we have properties attribute (with type=None)
            self._store_unknown_attrs_as_properties = (
                hasattr(self.__class__, 'properties')
                and self.__class__.properties.type is None
            )

        self._update_location()

        for attr, component in self._attributes_iterator():
            if component.aka:
                # Register alias for the attribute (local name)
                self._attr_aliases[component.aka] = attr

        # TODO(mordred) This is terrible, but is a hack at the moment to ensure
        # json.dumps works. The json library does basically if not obj: and
        # obj.items() ... but I think the if not obj: is short-circuiting down
        # in the C code and thus since we don't store the data in self[] it's
        # always False even if we override __len__ or __bool__.
        dict.update(self, self.to_dict())

    @classmethod
    def _attributes_iterator(cls, components=tuple([Body, Header])):
        """Iterator over all Resource attributes
        """
        # isinstance stricly requires this to be a tuple
        # Since we're looking at class definitions we need to include
        # subclasses, so check the whole MRO.
        for klass in cls.__mro__:
            for attr, component in klass.__dict__.items():
                if isinstance(component, components):
                    yield attr, component

    def __repr__(self):
        pairs = [
            "%s=%s" % (k, v if v is not None else 'None')
            for k, v in dict(itertools.chain(
                self._body.attributes.items(),
                self._header.attributes.items(),
                self._uri.attributes.items(),
                self._computed.attributes.items())).items()
        ]
        args = ", ".join(pairs)

        return "%s.%s(%s)" % (
            self.__module__, self.__class__.__name__, args)

    def __eq__(self, comparand):
        """Return True if another resource has the same contents"""
        if not isinstance(comparand, Resource):
            return False
        return all([
            self._body.attributes == comparand._body.attributes,
            self._header.attributes == comparand._header.attributes,
            self._uri.attributes == comparand._uri.attributes,
            self._computed.attributes == comparand._computed.attributes
        ])

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
            try:
                return object.__getattribute__(self, name)
            except AttributeError as e:
                if name in self._attr_aliases:
                    # Hmm - not found. But hey, the alias exists...
                    return object.__getattribute__(
                        self, self._attr_aliases[name])
                raise e

    def __getitem__(self, name):
        """Provide dictionary access for elements of the data model."""
        # Check the class, since BaseComponent is a descriptor and thus
        # behaves like its wrapped content. If we get it on the class,
        # it returns the BaseComponent itself, not the results of __get__.
        real_item = getattr(self.__class__, name, None)
        if not real_item and name in self._attr_aliases:
            # Not found? But we know an alias exists.
            name = self._attr_aliases[name]
            real_item = getattr(self.__class__, name, None)
        if isinstance(real_item, _BaseComponent):
            return getattr(self, name)
        raise KeyError(name)

    def __delitem__(self, name):
        delattr(self, name)

    def __setitem__(self, name, value):
        real_item = getattr(self.__class__, name, None)
        if isinstance(real_item, _BaseComponent):
            self.__setattr__(name, value)
        else:
            raise KeyError(
                "{name} is not found. {module}.{cls} objects do not support"
                " setting arbitrary keys through the"
                " dict interface.".format(
                    module=self.__module__,
                    cls=self.__class__.__name__,
                    name=name))

    def _attributes(self, remote_names=False, components=None,
                    include_aliases=True):
        """Generate list of supported attributes
        """
        attributes = []

        if not components:
            components = tuple([Body, Header, Computed, URI])

        for attr, component in self._attributes_iterator(components):
            key = attr if not remote_names else component.name
            attributes.append(key)
            if include_aliases and component.aka:
                attributes.append(component.aka)

        return attributes

    def keys(self):
        # NOTE(mordred) In python2, dict.keys returns a list. In python3 it
        # returns a dict_keys view. For 2, we can return a list from the
        # itertools chain. In 3, return the chain so it's at least an iterator.
        # It won't strictly speaking be an actual dict_keys, so it's possible
        # we may want to get more clever, but for now let's see how far this
        # will take us.
        # NOTE(gtema) For now let's return list of 'public' attributes and not
        # remotes or "unknown"
        return self._attributes()

    def items(self):
        # This method is critically required for Ansible "jsonify"
        # NOTE(gtema) For some reason when running from SDK itself the native
        # implementation of the method is absolutely sifficient, when called
        # from Ansible - the values are often empty. Even integrating all
        # Ansible internal methods did not help to find the root cause. Another
        # fact is that under Py2 everything is fine, while under Py3 it fails.
        # There is currently no direct test for Ansible-SDK issue. It is tested
        # implicitely in the keypair role for ansible module, where an assert
        # verifies presence of attributes.
        res = []
        for attr in self._attributes():
            # Append key, value tuple to result list
            res.append((attr, self[attr]))
        return res

    def _update(self, **attrs):
        """Given attributes, update them on this instance

        This is intended to be used from within the proxy
        layer when updating instances that may have already
        been created.
        """
        self.microversion = attrs.pop('microversion', None)
        body, header, uri, computed = self._collect_attrs(attrs)

        self._body.update(body)
        self._header.update(header)
        self._uri.update(uri)
        self._computed.update(computed)
        self._update_location()

        # TODO(mordred) This is terrible, but is a hack at the moment to ensure
        # json.dumps works. The json library does basically if not obj: and
        # obj.items() ... but I think the if not obj: is short-circuiting down
        # in the C code and thus since we don't store the data in self[] it's
        # always False even if we override __len__ or __bool__.
        dict.update(self, self.to_dict())

    def _collect_attrs(self, attrs):
        """Given attributes, return a dict per type of attribute

        This method splits up **attrs into separate dictionaries
        that correspond to the relevant body, header, and uri
        attributes that exist on this class.
        """
        body = self._consume_body_attrs(attrs)
        header = self._consume_header_attrs(attrs)
        uri = self._consume_uri_attrs(attrs)

        if attrs and self._store_unknown_attrs_as_properties:
            # Keep also remaining (unknown) attributes
            body = self._pack_attrs_under_properties(body, attrs)

        if any([body, header, uri]):
            attrs = self._compute_attributes(body, header, uri)

            body.update(self._consume_attrs(self._body_mapping(), attrs))

            header.update(self._consume_attrs(self._header_mapping(), attrs))
            uri.update(self._consume_attrs(self._uri_mapping(), attrs))
        computed = self._consume_attrs(self._computed_mapping(), attrs)
        # TODO(mordred) We should make a Location Resource and add it here
        # instead of just the dict.
        if self._connection:
            computed.setdefault('location', self._connection.current_location)

        return body, header, uri, computed

    def _update_location(self):
        """Update location to include resource project/zone information.

        Location should describe the location of the resource. For some
        resources, where the resource doesn't have any such baked-in notion
        we assume the resource exists in the same project as the logged-in
        user's token.

        However, if a resource contains a project_id, then that project is
        where the resource lives, and the location should reflect that.
        """
        if not self._connection:
            return
        kwargs = {}
        if hasattr(self, 'project_id'):
            kwargs['project_id'] = self.project_id
        if hasattr(self, 'availability_zone'):
            kwargs['zone'] = self.availability_zone
        if kwargs:
            self.location = self._connection._get_current_location(**kwargs)

    def _compute_attributes(self, body, header, uri):
        """Compute additional attributes from the remote resource."""
        return {}

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

    def _clean_body_attrs(self, attrs):
        """Mark the attributes as up-to-date."""
        self._body.clean(only=attrs)
        if self.commit_jsonpatch or self.allow_patch:
            for attr in attrs:
                if attr in self._body:
                    self._original_body[attr] = self._body[attr]

    @classmethod
    def _get_mapping(cls, component):
        """Return a dict of attributes of a given component on the class"""
        mapping = component._map_cls()
        ret = component._map_cls()
        for key, value in cls._attributes_iterator(component):
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
    def _computed_mapping(cls):
        """Return all URI members of this class"""
        return cls._get_mapping(Computed)

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
    def existing(cls, connection=None, **kwargs):
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
        return cls(_synchronized=True, connection=connection, **kwargs)

    @classmethod
    def _from_munch(cls, obj, synchronized=True, connection=None):
        """Create an instance from a ``munch.Munch`` object.

        This is intended as a temporary measure to convert between shade-style
        Munch objects and original openstacksdk resources.

        :param obj: a ``munch.Munch`` object to convert from.
        :param bool synchronized: whether this object already exists on server
            Must be set to ``False`` for newly created objects.
        """
        return cls(_synchronized=synchronized, connection=connection, **obj)

    def to_dict(self, body=True, headers=True, computed=True,
                ignore_none=False, original_names=False, _to_munch=False):
        """Return a dictionary of this resource's contents

        :param bool body: Include the :class:`~openstack.resource.Body`
                          attributes in the returned dictionary.
        :param bool headers: Include the :class:`~openstack.resource.Header`
                             attributes in the returned dictionary.
        :param bool computed: Include the :class:`~openstack.resource.Computed`
                              attributes in the returned dictionary.
        :param bool ignore_none: When True, exclude key/value pairs where
                                 the value is None. This will exclude
                                 attributes that the server hasn't returned.
        :param bool original_names: When True, use attribute names as they
                                    were received from the server.
        :param bool _to_munch: For internal use only. Converts to `munch.Munch`
                               instead of dict.

        :return: A dictionary of key/value pairs where keys are named
                 as they exist as attributes of this class.
        """
        if _to_munch:
            mapping = munch.Munch()
        else:
            mapping = {}

        components = []
        if body:
            components.append(Body)
        if headers:
            components.append(Header)
        if computed:
            components.append(Computed)
        if not components:
            raise ValueError(
                "At least one of `body`, `headers` or `computed` must be True")

        # isinstance stricly requires this to be a tuple
        components = tuple(components)

        # NOTE: This is similar to the implementation in _get_mapping
        # but is slightly different in that we're looking at an instance
        # and we're mapping names on this class to their actual stored
        # values.
        for attr, component in self._attributes_iterator(components):
            if original_names:
                key = component.name
            else:
                key = attr
            for key in filter(None, (key, component.aka)):
                # Make sure base classes don't end up overwriting
                # mappings we've found previously in subclasses.
                if key not in mapping:
                    value = getattr(self, attr, None)
                    if ignore_none and value is None:
                        continue
                    if isinstance(value, Resource):
                        mapping[key] = value.to_dict(_to_munch=_to_munch)
                    elif isinstance(value, dict) and _to_munch:
                        mapping[key] = munch.Munch(value)
                    elif value and isinstance(value, list):
                        converted = []
                        for raw in value:
                            if isinstance(raw, Resource):
                                converted.append(
                                    raw.to_dict(_to_munch=_to_munch))
                            elif isinstance(raw, dict) and _to_munch:
                                converted.append(munch.Munch(raw))
                            else:
                                converted.append(raw)
                        mapping[key] = converted
                    else:
                        mapping[key] = value

        return mapping
    # Compatibility with the munch.Munch.toDict method
    toDict = to_dict
    # Make the munch copy method use to_dict
    copy = to_dict

    def _to_munch(self, original_names=True):
        """Convert this resource into a Munch compatible with shade."""
        return self.to_dict(
            body=True, headers=False,
            original_names=original_names, _to_munch=True)

    def _unpack_properties_to_resource_root(self, body):
        if not body:
            return
        # We do not want to modify caller
        body = body.copy()
        props = body.pop('properties', {})
        if props and isinstance(props, dict):
            # unpack dict of properties back to the root of the resource
            body.update(props)
        elif props and isinstance(props, str):
            # A string value only - bring it back
            body['properties'] = props
        return body

    def _pack_attrs_under_properties(self, body, attrs):
        props = body.get('properties', {})
        if not isinstance(props, dict):
            props = {'properties': props}
        props.update(attrs)
        body['properties'] = props
        return body

    def _prepare_request_body(self, patch, prepend_key):
        if patch:
            if not self._store_unknown_attrs_as_properties:
                # Default case
                new = self._body.attributes
                original_body = self._original_body
            else:
                new = self._unpack_properties_to_resource_root(
                    self._body.attributes)
                original_body = self._unpack_properties_to_resource_root(
                    self._original_body)

            # NOTE(gtema) sort result, since we might need validate it in tests
            body = sorted(
                list(jsonpatch.make_patch(
                    original_body,
                    new).patch),
                key=operator.itemgetter('path')
            )
        else:
            if not self._store_unknown_attrs_as_properties:
                # Default case
                body = self._body.dirty
            else:
                body = self._unpack_properties_to_resource_root(
                    self._body.dirty)

            if prepend_key and self.resource_key is not None:
                body = {self.resource_key: body}
        return body

    def _prepare_request(self, requires_id=None, prepend_key=False,
                         patch=False, base_path=None):
        """Prepare a request to be sent to the server

        Create operations don't require an ID, but all others do,
        so only try to append an ID when it's needed with
        requires_id. Create and update operations sometimes require
        their bodies to be contained within an dict -- if the
        instance contains a resource_key and prepend_key=True,
        the body will be wrapped in a dict with that key.
        If patch=True, a JSON patch is prepared instead of the full body.

        Return a _Request object that contains the constructed URI
        as well a body and headers that are ready to send.
        Only dirty body and header contents will be returned.
        """
        if requires_id is None:
            requires_id = self.requires_id

        body = self._prepare_request_body(patch, prepend_key)

        # TODO(mordred) Ensure headers have string values better than this
        headers = {}
        for k, v in self._header.dirty.items():
            if isinstance(v, list):
                headers[k] = ", ".join(v)
            else:
                headers[k] = str(v)

        if base_path is None:
            base_path = self.base_path
        uri = base_path % self._uri.attributes
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
            try:
                body = response.json()
                if self.resource_key and self.resource_key in body:
                    body = body[self.resource_key]

                body_attrs = self._consume_body_attrs(body)

                if self._store_unknown_attrs_as_properties:
                    body_attrs = self._pack_attrs_under_properties(
                        body_attrs, body)

                self._body.attributes.update(body_attrs)
                self._body.clean()
                if self.commit_jsonpatch or self.allow_patch:
                    # We need the original body to compare against
                    self._original_body = body_attrs.copy()
            except ValueError:
                # Server returned not parse-able response (202, 204, etc)
                # Do simply nothing
                pass

        headers = self._consume_header_attrs(response.headers)
        self._header.attributes.update(headers)
        self._header.clean()
        self._update_location()
        dict.update(self, self.to_dict())

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

    @classmethod
    def _get_microversion_for_list(cls, session):
        """Get microversion to use when listing resources.

        The base version uses the following logic:
        1. If the session has a default microversion for the current service,
           just use it.
        2. If ``self._max_microversion`` is not ``None``, use minimum between
           it and the maximum microversion supported by the server.
        3. Otherwise use ``None``.

        Subclasses can override this method if more complex logic is needed.

        :param session: :class`keystoneauth1.adapter.Adapter`
        :return: microversion as string or ``None``
        """
        if session.default_microversion:
            return session.default_microversion

        return utils.maximum_supported_microversion(session,
                                                    cls._max_microversion)

    def _get_microversion_for(self, session, action):
        """Get microversion to use for the given action.

        The base version uses :meth:`_get_microversion_for_list`.
        Subclasses can override this method if more complex logic is needed.

        :param session: :class`keystoneauth1.adapter.Adapter`
        :param action: One of "fetch", "commit", "create", "delete", "patch".
            Unused in the base implementation.
        :return: microversion as string or ``None``
        """
        if action not in ('fetch', 'commit', 'create', 'delete', 'patch'):
            raise ValueError('Invalid action: %s' % action)

        return self._get_microversion_for_list(session)

    def _assert_microversion_for(self, session, action, expected,
                                 error_message=None):
        """Enforce that the microversion for action satisfies the requirement.

        :param session: :class`keystoneauth1.adapter.Adapter`
        :param action: One of "fetch", "commit", "create", "delete".
        :param expected: Expected microversion.
        :param error_message: Optional error message with details. Will be
            prepended to the message generated here.
        :return: resulting microversion as string.
        :raises: :exc:`~openstack.exceptions.NotSupported` if the version
            used for the action is lower than the expected one.
        """
        def _raise(message):
            if error_message:
                error_message.rstrip('.')
                message = '%s. %s' % (error_message, message)

            raise exceptions.NotSupported(message)

        actual = self._get_microversion_for(session, action)
        if actual is None:
            message = ("API version %s is required, but the default "
                       "version will be used.") % expected
            _raise(message)

        actual_n = discover.normalize_version_number(actual)
        expected_n = discover.normalize_version_number(expected)
        if actual_n < expected_n:
            message = ("API version %(expected)s is required, but %(actual)s "
                       "will be used.") % {'expected': expected,
                                           'actual': actual}
            _raise(message)

        return actual

    def create(self, session, prepend_key=True, base_path=None, **params):
        """Create a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param prepend_key: A boolean indicating whether the resource_key
                            should be prepended in a resource creation
                            request. Default to True.
        :param str base_path: Base part of the URI for creating resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.
        :param dict params: Additional params to pass.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_create` is not set to ``True``.
        """
        if not self.allow_create:
            raise exceptions.MethodNotSupported(self, "create")

        session = self._get_session(session)
        microversion = self._get_microversion_for(session, 'create')
        requires_id = (self.create_requires_id
                       if self.create_requires_id is not None
                       else self.create_method == 'PUT')
        if self.create_method == 'PUT':
            request = self._prepare_request(requires_id=requires_id,
                                            prepend_key=prepend_key,
                                            base_path=base_path)
            response = session.put(request.url,
                                   json=request.body, headers=request.headers,
                                   microversion=microversion, params=params)
        elif self.create_method == 'POST':
            request = self._prepare_request(requires_id=requires_id,
                                            prepend_key=prepend_key,
                                            base_path=base_path)
            response = session.post(request.url,
                                    json=request.body, headers=request.headers,
                                    microversion=microversion, params=params)
        else:
            raise exceptions.ResourceFailure(
                msg="Invalid create method: %s" % self.create_method)

        has_body = (self.has_body if self.create_returns_body is None
                    else self.create_returns_body)
        self.microversion = microversion
        self._translate_response(response, has_body=has_body)
        # direct comparision to False since we need to rule out None
        if self.has_body and self.create_returns_body is False:
            # fetch the body if it's required but not returned by create
            return self.fetch(session)
        return self

    def fetch(self, session, requires_id=True,
              base_path=None, error_message=None, **params):
        """Get a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param boolean requires_id: A boolean indicating whether resource ID
                                    should be part of the requested URI.
        :param str base_path: Base part of the URI for fetching resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.
        :param str error_message: An Error message to be returned if
                                  requested object does not exist.
        :param dict params: Additional parameters that can be consumed.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_fetch` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.ResourceNotFound` if
                 the resource was not found.
        """
        if not self.allow_fetch:
            raise exceptions.MethodNotSupported(self, "fetch")

        request = self._prepare_request(requires_id=requires_id,
                                        base_path=base_path)
        session = self._get_session(session)
        microversion = self._get_microversion_for(session, 'fetch')
        response = session.get(request.url, microversion=microversion,
                               params=params)
        kwargs = {}
        if error_message:
            kwargs['error_message'] = error_message

        self.microversion = microversion
        self._translate_response(response, **kwargs)
        return self

    def head(self, session, base_path=None):
        """Get headers from a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param str base_path: Base part of the URI for fetching resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_head` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.ResourceNotFound` if
                 the resource was not found.
        """
        if not self.allow_head:
            raise exceptions.MethodNotSupported(self, "head")

        request = self._prepare_request(base_path=base_path)

        session = self._get_session(session)
        microversion = self._get_microversion_for(session, 'fetch')
        response = session.head(request.url,
                                microversion=microversion)

        self.microversion = microversion
        self._translate_response(response, has_body=False)
        return self

    @property
    def requires_commit(self):
        """Whether the next commit() call will do anything."""
        return (self._body.dirty or self._header.dirty
                or self.allow_empty_commit)

    def commit(self, session, prepend_key=True, has_body=True,
               retry_on_conflict=None, base_path=None):
        """Commit the state of the instance to the remote resource.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param prepend_key: A boolean indicating whether the resource_key
                            should be prepended in a resource update request.
                            Default to True.
        :param bool retry_on_conflict: Whether to enable retries on HTTP
                                       CONFLICT (409). Value of ``None`` leaves
                                       the `Adapter` defaults.
        :param str base_path: Base part of the URI for modifying resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_commit` is not set to ``True``.
        """
        # The id cannot be dirty for an commit
        self._body._dirty.discard("id")

        # Only try to update if we actually have anything to commit.
        if not self.requires_commit:
            return self

        if not self.allow_commit:
            raise exceptions.MethodNotSupported(self, "commit")

        # Avoid providing patch unconditionally to avoid breaking subclasses
        # without it.
        kwargs = {}
        if self.commit_jsonpatch:
            kwargs['patch'] = True

        request = self._prepare_request(prepend_key=prepend_key,
                                        base_path=base_path,
                                        **kwargs)
        microversion = self._get_microversion_for(session, 'commit')

        return self._commit(session, request, self.commit_method, microversion,
                            has_body=has_body,
                            retry_on_conflict=retry_on_conflict)

    def _commit(self, session, request, method, microversion, has_body=True,
                retry_on_conflict=None):
        session = self._get_session(session)

        kwargs = {}
        retriable_status_codes = set(session.retriable_status_codes or ())
        if retry_on_conflict:
            kwargs['retriable_status_codes'] = retriable_status_codes | {409}
        elif retry_on_conflict is not None and retriable_status_codes:
            # The baremetal proxy defaults to retrying on conflict, allow
            # overriding it via an explicit retry_on_conflict=False.
            kwargs['retriable_status_codes'] = retriable_status_codes - {409}

        try:
            call = getattr(session, method.lower())
        except AttributeError:
            raise exceptions.ResourceFailure(
                msg="Invalid commit method: %s" % method)

        response = call(request.url, json=request.body,
                        headers=request.headers, microversion=microversion,
                        **kwargs)

        self.microversion = microversion
        self._translate_response(response, has_body=has_body)
        return self

    def _convert_patch(self, patch):
        if not isinstance(patch, list):
            patch = [patch]

        converted = []
        for item in patch:
            try:
                path = item['path']
                parts = path.lstrip('/').split('/', 1)
                field = parts[0]
            except (KeyError, IndexError):
                raise ValueError("Malformed or missing path in %s" % item)

            try:
                component = getattr(self.__class__, field)
            except AttributeError:
                server_field = field
            else:
                server_field = component.name

            if len(parts) > 1:
                new_path = '/%s/%s' % (server_field, parts[1])
            else:
                new_path = '/%s' % server_field
            converted.append(dict(item, path=new_path))

        return converted

    def patch(self, session, patch=None, prepend_key=True, has_body=True,
              retry_on_conflict=None, base_path=None):
        """Patch the remote resource.

        Allows modifying the resource by providing a list of JSON patches to
        apply to it. The patches can use both the original (server-side) and
        SDK field names.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param patch: Additional JSON patch as a list or one patch item.
                      If provided, it is applied on top of any changes to the
                      current resource.
        :param prepend_key: A boolean indicating whether the resource_key
                            should be prepended in a resource update request.
                            Default to True.
        :param bool retry_on_conflict: Whether to enable retries on HTTP
                                       CONFLICT (409). Value of ``None`` leaves
                                       the `Adapter` defaults.
        :param str base_path: Base part of the URI for modifying resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_patch` is not set to ``True``.
        """
        # The id cannot be dirty for an commit
        self._body._dirty.discard("id")

        # Only try to update if we actually have anything to commit.
        if not patch and not self.requires_commit:
            return self

        if not self.allow_patch:
            raise exceptions.MethodNotSupported(self, "patch")

        request = self._prepare_request(prepend_key=prepend_key,
                                        base_path=base_path, patch=True)
        microversion = self._get_microversion_for(session, 'patch')
        if patch:
            request.body += self._convert_patch(patch)

        return self._commit(session, request, 'PATCH', microversion,
                            has_body=has_body,
                            retry_on_conflict=retry_on_conflict)

    def delete(self, session, error_message=None):
        """Delete the remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_commit` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.ResourceNotFound` if
                 the resource was not found.
        """

        response = self._raw_delete(session)
        kwargs = {}
        if error_message:
            kwargs['error_message'] = error_message

        self._translate_response(response, has_body=False, **kwargs)
        return self

    def _raw_delete(self, session):
        if not self.allow_delete:
            raise exceptions.MethodNotSupported(self, "delete")

        request = self._prepare_request()
        session = self._get_session(session)
        microversion = self._get_microversion_for(session, 'delete')

        return session.delete(
            request.url,
            microversion=microversion)

    @classmethod
    def list(cls, session, paginated=True, base_path=None,
             allow_unknown_params=False, **params):
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
        :param str base_path: Base part of the URI for listing resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param bool allow_unknown_params: ``True`` to accept, but discard
            unknown query parameters. This allows getting list of 'filters' and
            passing everything known to the server. ``False`` will result in
            validation exception when unknown query parameters are passed.
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
        microversion = cls._get_microversion_for_list(session)

        if base_path is None:
            base_path = cls.base_path
        params = cls._query_mapping._validate(
            params, base_path=base_path,
            allow_unknown_params=allow_unknown_params)
        query_params = cls._query_mapping._transpose(params, cls)
        uri = base_path % params

        limit = query_params.get('limit')

        # Track the total number of resources yielded so we can paginate
        # swift objects
        total_yielded = 0
        while uri:
            # Copy query_params due to weird mock unittest interactions
            response = session.get(
                uri,
                headers={"Accept": "application/json"},
                params=query_params.copy(),
                microversion=microversion)
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

                value = cls.existing(
                    microversion=microversion,
                    connection=session._get_connection(),
                    **raw_resource)
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
                pagination_key = 'links'
            if not pagination_key and cls.resources_key:
                # Nova has a {key}_links dict in the main body
                pagination_key = '{key}_links'.format(key=cls.resources_key)
            if pagination_key:
                links = data.get(pagination_key, {})
                # keystone might return a dict
                if isinstance(links, dict):
                    links = ({k: v} for k, v in six.iteritems(links))
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

        # Parse params from Link (next page URL) into params.
        # This prevents duplication of query parameters that with large
        # number of pages result in HTTP 414 error eventually.
        if next_link:
            parts = six.moves.urllib.parse.urlparse(next_link)
            query_params = six.moves.urllib.parse.parse_qs(parts.query)
            params.update(query_params)
            next_link = six.moves.urllib.parse.urljoin(next_link,
                                                       parts.path)

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
        session = cls._get_session(session)
        # Try to short-circuit by looking directly for a matching ID.
        try:
            match = cls.existing(
                id=name_or_id,
                connection=session._get_connection(),
                **params)
            return match.fetch(session, **params)
        except exceptions.NotFoundException:
            pass

        if ('name' in cls._query_mapping._mapping.keys()
                and 'name' not in params):
            params['name'] = name_or_id

        data = cls.list(session, **params)

        result = cls._get_one_match(name_or_id, data)
        if result is not None:
            return result

        if ignore_missing:
            return None
        raise exceptions.ResourceNotFound(
            "No %s found for %s" % (cls.__name__, name_or_id))


class TagMixin(object):

    _tag_query_parameters = {
        'tags': 'tags',
        'any_tags': 'tags-any',
        'not_tags': 'not-tags',
        'not_any_tags': 'not-tags-any',
    }

    #: A list of associated tags
    #: *Type: list of tag strings*
    tags = Body('tags', type=list, default=[])

    def fetch_tags(self, session):
        """Lists tags set on the entity.

        :param session: The session to use for making this request.
        :return: The list with tags attached to the entity
        """
        url = utils.urljoin(self.base_path, self.id, 'tags')
        session = self._get_session(session)
        response = session.get(url)
        exceptions.raise_from_response(response)
        # NOTE(gtema): since this is a common method
        # we can't rely on the resource_key, because tags are returned
        # without resource_key. Do parse response here
        json = response.json()
        if 'tags' in json:
            self._body.attributes.update({'tags': json['tags']})
        return self

    def set_tags(self, session, tags=[]):
        """Sets/Replaces all tags on the resource.

        :param session: The session to use for making this request.
        :param list tags: List with tags to be set on the resource
        """
        url = utils.urljoin(self.base_path, self.id, 'tags')
        session = self._get_session(session)
        response = session.put(url, json={'tags': tags})
        exceptions.raise_from_response(response)
        self._body.attributes.update({'tags': tags})
        return self

    def remove_all_tags(self, session):
        """Removes all tags on the entity.

        :param session: The session to use for making this request.
        """
        url = utils.urljoin(self.base_path, self.id, 'tags')
        session = self._get_session(session)
        response = session.delete(url)
        exceptions.raise_from_response(response)
        self._body.attributes.update({'tags': []})
        return self

    def check_tag(self, session, tag):
        """Checks if tag exists on the entity.

        If the tag does not exist a 404 will be returned

        :param session: The session to use for making this request.
        :param tag: The tag as a string.
        """
        url = utils.urljoin(self.base_path, self.id, 'tags', tag)
        session = self._get_session(session)
        response = session.get(url)
        exceptions.raise_from_response(response,
                                       error_message='Tag does not exist')
        return self

    def add_tag(self, session, tag):
        """Adds a single tag to the resource.

        :param session: The session to use for making this request.
        :param tag: The tag as a string.
        """
        url = utils.urljoin(self.base_path, self.id, 'tags', tag)
        session = self._get_session(session)
        response = session.put(url)
        exceptions.raise_from_response(response)
        # we do not want to update tags directly
        tags = self.tags
        tags.append(tag)
        self._body.attributes.update({
            'tags': tags
        })
        return self

    def remove_tag(self, session, tag):
        """Removes a single tag from the specified server.

        :param session: The session to use for making this request.
        :param tag: The tag as a string.
        """
        url = utils.urljoin(self.base_path, self.id, 'tags', tag)
        session = self._get_session(session)
        response = session.delete(url)
        exceptions.raise_from_response(response)
        # we do not want to update tags directly
        tags = self.tags
        try:
            # NOTE(gtema): if tags were not fetched, but request suceeded
            # it is ok. Just ensure tag does not exist locally
            tags.remove(tag)
        except ValueError:
            pass  # do nothing!
        self._body.attributes.update({
            'tags': tags
        })
        return self


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
        resource = resource.fetch(session)

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
            resource = resource.fetch(session)
            if not resource:
                return orig_resource
            if resource.status.lower() == 'deleted':
                return resource
        except exceptions.NotFoundException:
            return orig_resource
