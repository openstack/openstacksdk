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

"""Base resource class.

The :class:`~openstack.resource.Resource` class is a base
class that represent a remote resource. The attributes that
comprise a request or response for this resource are specified
as class members on the Resource subclass where their values
are of a component type, including :class:`~openstack.fields.Body`,
:class:`~openstack.fields.Header`, and :class:`~openstack.fields.URI`.

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
import operator
import typing as ty
import typing_extensions as ty_ext
import urllib.parse
import warnings

import jsonpatch
from keystoneauth1 import adapter
from keystoneauth1 import discover

from openstack import _log
from openstack import exceptions
from openstack import fields
from openstack import utils
from openstack import warnings as os_warnings

if ty.TYPE_CHECKING:
    from openstack import connection

LOG = _log.setup_logging(__name__)

AdapterT = ty.TypeVar('AdapterT', bound=adapter.Adapter)
ResourceT = ty.TypeVar('ResourceT', bound='Resource')


# TODO(stephenfin): We should deprecate the 'type' and 'list_type' arguments
# for all of the below in favour of annotations. To that end, we have stuck
# with Any rather than generating super complex types
def Body(
    name: str,
    type: ty.Optional[ty.Any] = None,
    default: ty.Any = None,
    alias: ty.Optional[str] = None,
    aka: ty.Optional[str] = None,
    alternate_id: bool = False,
    list_type: ty.Optional[ty.Any] = None,
    coerce_to_default: bool = False,
    deprecated: bool = False,
    deprecation_reason: ty.Optional[str] = None,
) -> ty.Any:
    return fields.Body(
        name,
        type=type,
        default=default,
        alias=alias,
        aka=aka,
        alternate_id=alternate_id,
        list_type=list_type,
        coerce_to_default=coerce_to_default,
        deprecated=deprecated,
        deprecation_reason=deprecation_reason,
    )


def Header(
    name: str,
    type: ty.Optional[ty.Any] = None,
    default: ty.Any = None,
    alias: ty.Optional[str] = None,
    aka: ty.Optional[str] = None,
    alternate_id: bool = False,
    list_type: ty.Optional[ty.Any] = None,
    coerce_to_default: bool = False,
    deprecated: bool = False,
    deprecation_reason: ty.Optional[str] = None,
) -> ty.Any:
    return fields.Header(
        name,
        type=type,
        default=default,
        alias=alias,
        aka=aka,
        alternate_id=alternate_id,
        list_type=list_type,
        coerce_to_default=coerce_to_default,
        deprecated=deprecated,
        deprecation_reason=deprecation_reason,
    )


def URI(
    name: str,
    type: ty.Optional[ty.Any] = None,
    default: ty.Any = None,
    alias: ty.Optional[str] = None,
    aka: ty.Optional[str] = None,
    alternate_id: bool = False,
    list_type: ty.Optional[ty.Any] = None,
    coerce_to_default: bool = False,
    deprecated: bool = False,
    deprecation_reason: ty.Optional[str] = None,
) -> ty.Any:
    return fields.URI(
        name,
        type=type,
        default=default,
        alias=alias,
        aka=aka,
        alternate_id=alternate_id,
        list_type=list_type,
        coerce_to_default=coerce_to_default,
        deprecated=deprecated,
        deprecation_reason=deprecation_reason,
    )


def Computed(
    name: str,
    type: ty.Optional[ty.Any] = None,
    default: ty.Any = None,
    alias: ty.Optional[str] = None,
    aka: ty.Optional[str] = None,
    alternate_id: bool = False,
    list_type: ty.Optional[ty.Any] = None,
    coerce_to_default: bool = False,
    deprecated: bool = False,
    deprecation_reason: ty.Optional[str] = None,
) -> ty.Any:
    return fields.Computed(
        name,
        type=type,
        default=default,
        alias=alias,
        aka=aka,
        alternate_id=alternate_id,
        list_type=list_type,
        coerce_to_default=coerce_to_default,
        deprecated=deprecated,
        deprecation_reason=deprecation_reason,
    )


class _ComponentManager(collections.abc.MutableMapping):
    """Storage of a component type"""

    attributes: dict[str, ty.Any]

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
        return {key: self.attributes.get(key, None) for key in self._dirty}

    def clean(self, only=None):
        """Signal that the resource no longer has modified attributes.

        :param only: an optional set of attributes to no longer consider
            changed
        """
        if only:
            self._dirty = self._dirty - set(only)
        else:
            self._dirty = set()


class _Request:
    """Prepared components that go into a KSA request"""

    def __init__(self, url, body, headers):
        self.url = url
        self.body = body
        self.headers = headers


class QueryParameters:
    def __init__(
        self,
        *names,
        include_pagination_defaults=True,
        **mappings,
    ):
        """Create a dict of accepted query parameters

        :param names: List of strings containing client-side query parameter
            names. Each name in the list maps directly to the name
            expected by the server.
        :param mappings: Key-value pairs where the key is the client-side
            name we'll accept here and the value is the name
            the server expects, e.g, ``changes_since=changes-since``.
            Additionally, a value can be a dict with optional keys:

            - ``name`` - server-side name,
            - ``type`` - callable to convert from client to server
              representation
        :param include_pagination_defaults: If true, include default pagination
            parameters, ``limit`` and ``marker``. These are the most common
            query parameters used for listing resources in OpenStack APIs.
        """
        self._mapping: dict[str, ty.Union[str, dict]] = {}
        if include_pagination_defaults:
            self._mapping.update({"limit": "limit", "marker": "marker"})
        self._mapping.update({name: name for name in names})
        self._mapping.update(mappings)

    def _validate(self, query, base_path=None, allow_unknown_params=False):
        """Check that supplied query keys match known query mappings

        :param dict query: Collection of key-value pairs where each key is the
            client-side parameter name or server side name.
        :param base_path: Formatted python string of the base url path for
            the resource.
        :param allow_unknown_params: Exclude query params not known by the
            resource.

        :returns: Filtered collection of the supported QueryParameters
        """
        expected_params = list(self._mapping)
        expected_params.extend(
            value.get('name', key) if isinstance(value, dict) else value
            for key, value in self._mapping.items()
        )

        if base_path:
            expected_params += utils.get_string_format_keys(base_path)

        invalid_keys = set(query) - set(expected_params)
        if not invalid_keys:
            return query
        else:
            if not allow_unknown_params:
                raise exceptions.InvalidResourceQuery(
                    message="Invalid query params: {}".format(
                        ",".join(invalid_keys)
                    ),
                    extra_data=invalid_keys,
                )
            else:
                known_keys = set(query).intersection(set(expected_params))
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
                    len(inspect.getfullargspec(type_).args) > 1
                )
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
    resource_key: ty.Optional[str] = None
    #: Plural form of key for resource.
    resources_key: ty.Optional[str] = None
    #: Key used for pagination links
    pagination_key: ty.Optional[str] = None

    #: The ID of this resource.
    id: str = Body("id")

    #: The name of this resource.
    name: str = Body("name")
    #: The OpenStack location of this resource.
    location: dict[str, ty.Any] = Computed('location')

    #: Mapping of accepted query parameter names.
    _query_mapping = QueryParameters()

    #: The base part of the URI for this resource.
    base_path: str = ""

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
    create_requires_id: ty.Optional[bool] = None
    #: Whether create should exclude ID in the body of the request.
    create_exclude_id_from_body = False
    #: Do responses for this resource have bodies
    has_body = True
    #: Does create returns a body (if False requires ID), defaults to has_body
    create_returns_body: ty.Optional[bool] = None

    #: Maximum microversion to use for getting/creating/updating the Resource
    _max_microversion: ty.Optional[str] = None
    #: API microversion (string or None) this Resource was loaded with
    microversion = None

    _connection = None
    _body: _ComponentManager
    _header: _ComponentManager
    _uri: _ComponentManager
    _computed: _ComponentManager
    _original_body: dict[str, ty.Any] = {}
    _store_unknown_attrs_as_properties = False
    _allow_unknown_attrs_in_body = False
    _unknown_attrs_in_body: dict[str, ty.Any] = {}

    # Placeholder for aliases as dict of {__alias__:__original}
    _attr_aliases: dict[str, str] = {}

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

        self._unknown_attrs_in_body = {}

        # NOTE: _collect_attrs modifies **attrs in place, removing
        # items as they match up with any of the body, header,
        # or uri mappings.
        body, header, uri, computed = self._collect_attrs(attrs)

        if self._allow_unknown_attrs_in_body:
            self._unknown_attrs_in_body.update(attrs)

        self._body = _ComponentManager(
            attributes=body, synchronized=_synchronized
        )
        self._header = _ComponentManager(
            attributes=header, synchronized=_synchronized
        )
        self._uri = _ComponentManager(
            attributes=uri, synchronized=_synchronized
        )
        self._computed = _ComponentManager(
            attributes=computed, synchronized=_synchronized
        )
        if self.commit_jsonpatch or self.allow_patch:
            # We need the original body to compare against
            if _synchronized:
                self._original_body = self._body.attributes.copy()
            elif self.id:
                # Never record ID as dirty.
                self._original_body = {self._alternate_id() or 'id': self.id}
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
    def _attributes_iterator(
        cls, components=tuple([fields.Body, fields.Header])
    ):
        """Iterator over all Resource attributes"""
        # isinstance stricly requires this to be a tuple
        # Since we're looking at class definitions we need to include
        # subclasses, so check the whole MRO.
        for klass in cls.__mro__:
            for attr, component in klass.__dict__.items():
                if isinstance(component, components):
                    yield attr, component

    def __repr__(self):
        pairs = [
            "{}={}".format(k, v if v is not None else 'None')
            for k, v in dict(
                itertools.chain(
                    self._body.attributes.items(),
                    self._header.attributes.items(),
                    self._uri.attributes.items(),
                    self._computed.attributes.items(),
                )
            ).items()
        ]
        args = ", ".join(pairs)

        return f"{self.__module__}.{self.__class__.__name__}({args})"

    def __eq__(self, comparand):
        """Return True if another resource has the same contents"""
        if not isinstance(comparand, Resource):
            return False
        return all(
            [
                self._body.attributes == comparand._body.attributes,
                self._header.attributes == comparand._header.attributes,
                self._uri.attributes == comparand._uri.attributes,
                self._computed.attributes == comparand._computed.attributes,
            ]
        )

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
                key = self._alternate_id()
                if key:
                    return self._body.get(key)
        else:
            try:
                return object.__getattribute__(self, name)
            except AttributeError as e:
                if name in self._attr_aliases:
                    # Hmm - not found. But hey, the alias exists...
                    return object.__getattribute__(
                        self, self._attr_aliases[name]
                    )
                if self._allow_unknown_attrs_in_body:
                    # Last chance, maybe it's in body as attribute which isn't
                    # in the mapping at all...
                    if name in self._unknown_attrs_in_body:
                        return self._unknown_attrs_in_body[name]
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
        if isinstance(real_item, fields._BaseComponent):
            return getattr(self, name)
        if not real_item:
            # In order to maintain backwards compatibility where we were
            # returning Munch (and server side names) and Resource object with
            # normalized attributes we can offer dict access via server side
            # names.
            for attr, component in self._attributes_iterator((fields.Body,)):
                if component.name == name:
                    warnings.warn(
                        f"Access to '{self.__class__}[{name}]' is deprecated. "
                        f"Use '{self.__class__}.{attr}' attribute instead",
                        os_warnings.LegacyAPIWarning,
                    )
                    return getattr(self, attr)
            if self._allow_unknown_attrs_in_body:
                if name in self._unknown_attrs_in_body:
                    return self._unknown_attrs_in_body[name]
        raise KeyError(name)

    def __delitem__(self, name):
        delattr(self, name)

    def __setitem__(self, name, value):
        real_item = getattr(self.__class__, name, None)
        if isinstance(real_item, fields._BaseComponent):
            self.__setattr__(name, value)
        else:
            if self._allow_unknown_attrs_in_body:
                self._unknown_attrs_in_body[name] = value
                return
            raise KeyError(
                f"{name} is not found. "
                f"{self.__module__}.{self.__class__.__name__} objects do not "
                f"support setting arbitrary keys through the dict interface."
            )

    def _attributes(
        self, remote_names=False, components=None, include_aliases=True
    ):
        """Generate list of supported attributes"""
        attributes = []

        if not components:
            components = (
                fields.Body,
                fields.Header,
                fields.Computed,
                fields.URI,
            )

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

    def _update(self, **attrs: ty.Any) -> None:
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

        if attrs:
            if self._allow_unknown_attrs_in_body:
                body.update(attrs)
            elif self._store_unknown_attrs_as_properties:
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
        return self._consume_mapped_attrs(fields.Body, attrs)

    def _consume_header_attrs(self, attrs):
        return self._consume_mapped_attrs(fields.Header, attrs)

    def _consume_uri_attrs(self, attrs):
        return self._consume_mapped_attrs(fields.URI, attrs)

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
        return cls._get_mapping(fields.Body)

    @classmethod
    def _header_mapping(cls):
        """Return all Header members of this class"""
        return cls._get_mapping(fields.Header)

    @classmethod
    def _uri_mapping(cls):
        """Return all URI members of this class"""
        return cls._get_mapping(fields.URI)

    @classmethod
    def _computed_mapping(cls):
        """Return all Computed members of this class"""
        return cls._get_mapping(fields.Computed)

    @classmethod
    def _alternate_id(cls):
        """Return the name of any value known as an alternate_id

        NOTE: This will only ever return the first such alternate_id.
        Only one alternate_id should be specified.

        Returns an empty string if no name exists, as this method is
        consumed by _get_id and passed to getattr.
        """
        for value in cls.__dict__.values():
            if isinstance(value, fields.Body):
                if value.alternate_id:
                    return value.name
        return ""

    @staticmethod
    def _get_id(value: ty.Union['Resource', str]) -> str:
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
    def new(cls, **kwargs: ty.Any) -> ty_ext.Self:
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
    def _from_munch(
        cls,
        obj: dict[str, ty.Union],
        synchronized: bool = True,
        connection: ty.Optional['connection.Connection'] = None,
    ) -> ty_ext.Self:
        """Create an instance from a ``utils.Munch`` object.

        This is intended as a temporary measure to convert between shade-style
        Munch objects and original openstacksdk resources.

        :param obj: a ``utils.Munch`` object to convert from.
        :param bool synchronized: whether this object already exists on server
            Must be set to ``False`` for newly created objects.
        """
        return cls(_synchronized=synchronized, connection=connection, **obj)

    def _attr_to_dict(self, attr, to_munch):
        """For a given attribute, convert it into a form suitable for a dict
        value.

        :param bool attr: Attribute name to convert

        :return: A dictionary of key/value pairs where keys are named
            as they exist as attributes of this class.
        :param bool _to_munch: Converts subresources to munch instead of dict.
        """
        value = getattr(self, attr, None)
        if isinstance(value, Resource):
            return value.to_dict(_to_munch=to_munch)
        elif isinstance(value, dict) and to_munch:
            return utils.Munch(value)
        elif value and isinstance(value, list):
            converted = []
            for raw in value:
                if isinstance(raw, Resource):
                    converted.append(raw.to_dict(_to_munch=to_munch))
                elif isinstance(raw, dict) and to_munch:
                    converted.append(utils.Munch(raw))
                else:
                    converted.append(raw)
            return converted
        return value

    def to_dict(
        self,
        body=True,
        headers=True,
        computed=True,
        ignore_none=False,
        original_names=False,
        _to_munch=False,
    ):
        """Return a dictionary of this resource's contents

        :param bool body: Include the :class:`~openstack.fields.Body`
            attributes in the returned dictionary.
        :param bool headers: Include the :class:`~openstack.fields.Header`
            attributes in the returned dictionary.
        :param bool computed: Include the :class:`~openstack.fields.Computed`
            attributes in the returned dictionary.
        :param bool ignore_none: When True, exclude key/value pairs where
            the value is None. This will exclude attributes that the server
            hasn't returned.
        :param bool original_names: When True, use attribute names as they
            were received from the server.
        :param bool _to_munch: For internal use only. Converts to `utils.Munch`
            instead of dict.

        :return: A dictionary of key/value pairs where keys are named
            as they exist as attributes of this class.
        """
        mapping: ty.Union[utils.Munch, dict]
        if _to_munch:
            mapping = utils.Munch()
        else:
            mapping = {}

        components: list[type[fields._BaseComponent]] = []
        if body:
            components.append(fields.Body)
        if headers:
            components.append(fields.Header)
        if computed:
            components.append(fields.Computed)
        if not components:
            raise ValueError(
                "At least one of `body`, `headers` or `computed` must be True"
            )

        if body and self._allow_unknown_attrs_in_body:
            for key in self._unknown_attrs_in_body:
                converted = self._attr_to_dict(
                    key,
                    to_munch=_to_munch,
                )
                if not ignore_none or converted is not None:
                    mapping[key] = converted

        # NOTE: This is similar to the implementation in _get_mapping
        # but is slightly different in that we're looking at an instance
        # and we're mapping names on this class to their actual stored
        # values.
        # NOTE: isinstance stricly requires components to be a tuple
        for attr, component in self._attributes_iterator(tuple(components)):
            if original_names:
                key = component.name
            else:
                key = attr
            for key in filter(None, (key, component.aka)):
                # Make sure base classes don't end up overwriting
                # mappings we've found previously in subclasses.
                if key not in mapping:
                    converted = self._attr_to_dict(
                        attr,
                        to_munch=_to_munch,
                    )
                    if ignore_none and converted is None:
                        continue
                    mapping[key] = converted

        return mapping

    # Compatibility with the utils.Munch.toDict method
    toDict = to_dict
    # Make the munch copy method use to_dict
    copy = to_dict

    def _to_munch(self, original_names=True):
        """Convert this resource into a Munch compatible with shade."""
        return self.to_dict(
            body=True,
            headers=False,
            original_names=original_names,
            _to_munch=True,
        )

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

    def _prepare_request_body(
        self,
        patch,
        prepend_key,
        *,
        resource_request_key=None,
    ):
        body: ty.Union[dict[str, ty.Any], list[ty.Any]]
        if patch:
            if not self._store_unknown_attrs_as_properties:
                # Default case
                new = self._body.attributes
                original_body = self._original_body
            else:
                new = self._unpack_properties_to_resource_root(
                    self._body.attributes
                )
                original_body = self._unpack_properties_to_resource_root(
                    self._original_body
                )

            # NOTE(gtema) sort result, since we might need validate it in tests
            body = sorted(
                list(jsonpatch.make_patch(original_body, new).patch),
                key=operator.itemgetter('path'),
            )
        else:
            if not self._store_unknown_attrs_as_properties:
                # Default case
                body = self._body.dirty
            else:
                body = self._unpack_properties_to_resource_root(
                    self._body.dirty
                )

            if prepend_key:
                if resource_request_key is not None:
                    body = {resource_request_key: body}
                elif self.resource_key is not None:
                    body = {self.resource_key: body}
        return body

    def _prepare_request(
        self,
        requires_id=None,
        prepend_key=False,
        patch=False,
        base_path=None,
        params=None,
        *,
        resource_request_key=None,
        **kwargs,
    ):
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

        # Conditionally construct arguments for _prepare_request_body
        request_kwargs = {"patch": patch, "prepend_key": prepend_key}
        if resource_request_key is not None:
            request_kwargs['resource_request_key'] = resource_request_key
        body = self._prepare_request_body(**request_kwargs)

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
                    "Request requires an ID but none was found"
                )

            uri = utils.urljoin(uri, self.id)

        if params:
            query_params = urllib.parse.urlencode(params)
            uri += '?' + query_params

        return _Request(uri, body, headers)

    def _translate_response(
        self,
        response,
        has_body=None,
        error_message=None,
        *,
        resource_response_key=None,
    ):
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
                if resource_response_key and resource_response_key in body:
                    body = body[resource_response_key]
                elif self.resource_key and self.resource_key in body:
                    body = body[self.resource_key]

                # Do not allow keys called "self" through. Glance chose
                # to name a key "self", so we need to pop it out because
                # we can't send it through cls.existing and into the
                # Resource initializer. "self" is already the first
                # argument and is practically a reserved word.
                body.pop("self", None)

                body_attrs = self._consume_body_attrs(body)
                if self._allow_unknown_attrs_in_body:
                    body_attrs.update(body)
                    self._unknown_attrs_in_body.update(body)
                elif self._store_unknown_attrs_as_properties:
                    body_attrs = self._pack_attrs_under_properties(
                        body_attrs, body
                    )

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
    def _get_session(cls, session: AdapterT) -> AdapterT:
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
        raise ValueError(
            "The session argument to Resource methods requires either an "
            "instance of an openstack.proxy.Proxy object or at the very least "
            "a raw keystoneauth1.adapter.Adapter."
        )

    @classmethod
    def _get_microversion(cls, session: adapter.Adapter) -> ty.Optional[str]:
        """Get microversion to use for the given action.

        The base version uses the following logic:

        1. If the session has a default microversion for the current service,
           just use it.
        2. If ``self._max_microversion`` is not ``None``, use minimum between
           it and the maximum microversion supported by the server.
        3. Otherwise use ``None``.

        Subclasses can override this method if more complex logic is needed.

        :param session: The session to use for making the request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :return: Microversion as string or ``None``
        """
        if session.default_microversion:
            return session.default_microversion

        return utils.maximum_supported_microversion(
            session, cls._max_microversion
        )

    @classmethod
    def _assert_microversion_for(
        cls,
        session: adapter.Adapter,
        expected: ty.Optional[str],
        *,
        error_message: ty.Optional[str] = None,
        maximum: ty.Optional[str] = None,
    ) -> str:
        """Enforce that the microversion for action satisfies the requirement.

        :param session: :class`keystoneauth1.adapter.Adapter`
        :param expected: Expected microversion.
        :param error_message: Optional error message with details. Will be
            prepended to the message generated here.
        :param maximum: Maximum microversion.
        :return: resulting microversion as string.
        :raises: :exc:`~openstack.exceptions.NotSupported` if the version
            used for the action is lower than the expected one.
        """

        def _raise(message: str) -> ty.NoReturn:
            if error_message:
                error_message.rstrip('.')
                message = f'{error_message}. {message}'

            raise exceptions.NotSupported(message)

        actual = cls._get_microversion(session)

        if actual is None:
            message = (
                f"API version {expected} is required, but the default "
                f"version will be used."
            )
            _raise(message)

        actual_n = discover.normalize_version_number(actual)

        if expected is not None:
            expected_n = discover.normalize_version_number(expected)
            if actual_n < expected_n:
                message = (
                    f"API version {expected} is required, but {actual} "
                    f"will be used."
                )
                _raise(message)

        if maximum is not None:
            maximum_n = discover.normalize_version_number(maximum)
            # Assume that if a service supports higher versions, it also
            # supports lower ones. Breaks for services that remove old API
            # versions (which is not something that has been done yet).
            if actual_n > maximum_n:
                return maximum

        return actual

    def create(
        self,
        session: adapter.Adapter,
        prepend_key: bool = True,
        base_path: ty.Optional[str] = None,
        *,
        resource_request_key: ty.Optional[str] = None,
        resource_response_key: ty.Optional[str] = None,
        microversion: ty.Optional[str] = None,
        **params: ty.Any,
    ) -> ty_ext.Self:
        """Create a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param prepend_key: A boolean indicating whether the resource_key
            should be prepended in a resource creation request. Default to
            True.
        :param str base_path: Base part of the URI for creating resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param str resource_request_key: Overrides the usage of
            self.resource_key when prepending a key to the request body.
            Ignored if `prepend_key` is false.
        :param str resource_response_key: Overrides the usage of
            self.resource_key when processing response bodies.
            Ignored if `prepend_key` is false.
        :param str microversion: API version to override the negotiated one.
        :param dict params: Additional params to pass.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_create` is not set to ``True``.
        """
        if not self.allow_create:
            raise exceptions.MethodNotSupported(self, 'create')

        session = self._get_session(session)
        if microversion is None:
            microversion = self._get_microversion(session)
        requires_id = (
            self.create_requires_id
            if self.create_requires_id is not None
            else self.create_method == 'PUT'
        )

        # Construct request arguments.
        request_kwargs = {
            "requires_id": requires_id,
            "prepend_key": prepend_key,
            "base_path": base_path,
        }
        if resource_request_key is not None:
            request_kwargs['resource_request_key'] = resource_request_key

        if self.create_exclude_id_from_body:
            self._body._dirty.discard("id")

        if self.create_method == 'PUT':
            request = self._prepare_request(**request_kwargs)
            response = session.put(
                request.url,
                json=request.body,
                headers=request.headers,
                microversion=microversion,
                params=params,
            )
        elif self.create_method == 'POST':
            request = self._prepare_request(**request_kwargs)
            response = session.post(
                request.url,
                json=request.body,
                headers=request.headers,
                microversion=microversion,
                params=params,
            )
        else:
            raise exceptions.ResourceFailure(
                f"Invalid create method: {self.create_method}"
            )

        has_body = (
            self.has_body
            if self.create_returns_body is None
            else self.create_returns_body
        )
        self.microversion = microversion

        self._translate_response(
            response,
            has_body=has_body,
            resource_response_key=resource_response_key,
        )
        # direct comparision to False since we need to rule out None
        if self.has_body and self.create_returns_body is False:
            # fetch the body if it's required but not returned by create
            return self.fetch(
                session,
                resource_response_key=resource_response_key,
            )
        return self

    @classmethod
    def bulk_create(
        cls,
        session: adapter.Adapter,
        data: list[dict[str, ty.Any]],
        prepend_key: bool = True,
        base_path: ty.Optional[str] = None,
        *,
        microversion: ty.Optional[str] = None,
        **params: ty.Any,
    ) -> ty.Generator[ty_ext.Self, None, None]:
        """Create multiple remote resources based on this class and data.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param data: list of dicts, which represent resources to create.
        :param prepend_key: A boolean indicating whether the resource_key
            should be prepended in a resource creation request. Default to
            True.
        :param str base_path: Base part of the URI for creating resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param str microversion: API version to override the negotiated one.
        :param dict params: Additional params to pass.

        :return: A generator of :class:`Resource` objects.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_create` is not set to ``True``.
        """
        if not cls.allow_create:
            raise exceptions.MethodNotSupported(cls, 'create')

        if not (
            data
            and isinstance(data, list)
            and all([isinstance(x, dict) for x in data])
        ):
            raise ValueError(f'Invalid data passed: {data}')

        session = cls._get_session(session)
        if microversion is None:
            microversion = cls._get_microversion(session)
        requires_id = (
            cls.create_requires_id
            if cls.create_requires_id is not None
            else cls.create_method == 'PUT'
        )
        if cls.create_method == 'PUT':
            method = session.put
        elif cls.create_method == 'POST':
            method = session.post
        else:
            raise exceptions.ResourceFailure(
                f"Invalid create method: {cls.create_method}"
            )

        _body: list[ty.Any] = []
        resources = []
        for attrs in data:
            # NOTE(gryf): we need to create resource objects, since
            # _prepare_request only works on instances, not classes.
            # Those objects will be used in case where request doesn't return
            # JSON data representing created resource, and yet it's required
            # to return newly created resource objects.
            # TODO(stephenfin): Our types say we accept a ksa Adapter, but this
            # requires an SDK Proxy. Do we update the types or rework this to
            # support use of an adapter.
            resource = cls.new(connection=session._get_connection(), **attrs)  # type: ignore
            resources.append(resource)
            request = resource._prepare_request(
                requires_id=requires_id, base_path=base_path
            )
            _body.append(request.body)

        body: ty.Union[dict[str, ty.Any], list[ty.Any]] = _body

        if prepend_key:
            if not cls.resources_key:
                raise exceptions.ResourceFailure(
                    "Cannot request prepend_key with Unset resources key"
                )

            body = {cls.resources_key: body}

        response = method(
            request.url,
            json=body,
            headers=request.headers,
            microversion=microversion,
            params=params,
        )
        exceptions.raise_from_response(response)
        json = response.json()

        if cls.resources_key:
            json = json[cls.resources_key]
        else:
            json = json

        if isinstance(data, list):
            json = json
        else:
            json = [json]

        has_body = (
            cls.has_body
            if cls.create_returns_body is None
            else cls.create_returns_body
        )
        if has_body and cls.create_returns_body is False:
            return (r.fetch(session) for r in resources)
        else:
            return (
                # TODO(stephenfin): Our types say we accept a ksa Adapter, but
                # this requires an SDK Proxy. Do we update the types or rework
                # this to support use of an adapter.
                cls.existing(
                    microversion=microversion,
                    connection=session._get_connection(),  # type: ignore
                    **res_dict,
                )
                for res_dict in json
            )

    def fetch(
        self,
        session: adapter.Adapter,
        requires_id: bool = True,
        base_path: ty.Optional[str] = None,
        error_message: ty.Optional[str] = None,
        skip_cache: bool = False,
        *,
        resource_response_key: ty.Optional[str] = None,
        microversion: ty.Optional[str] = None,
        **params: ty.Any,
    ) -> ty_ext.Self:
        """Get a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param boolean requires_id: A boolean indicating whether resource ID
            should be part of the requested URI.
        :param str base_path: Base part of the URI for fetching resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param str error_message: An Error message to be returned if
            requested object does not exist.
        :param bool skip_cache: A boolean indicating whether optional API
            cache should be skipped for this invocation.
        :param str resource_response_key: Overrides the usage of
            self.resource_key when processing the response body.
        :param str microversion: API version to override the negotiated one.
        :param dict params: Additional parameters that can be consumed.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_fetch` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.NotFoundException` if
            the resource was not found.
        """
        if not self.allow_fetch:
            raise exceptions.MethodNotSupported(self, 'fetch')

        request = self._prepare_request(
            requires_id=requires_id,
            base_path=base_path,
        )

        session = self._get_session(session)
        if microversion is None:
            microversion = self._get_microversion(session)
        self.microversion = microversion

        response = session.get(
            request.url,
            microversion=microversion,
            params=params,
            skip_cache=skip_cache,
        )

        self._translate_response(
            response,
            error_message=error_message,
            resource_response_key=resource_response_key,
        )

        return self

    def head(
        self,
        session: adapter.Adapter,
        base_path: ty.Optional[str] = None,
        *,
        microversion: ty.Optional[str] = None,
    ) -> ty_ext.Self:
        """Get headers from a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param str base_path: Base part of the URI for fetching resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param str microversion: API version to override the negotiated one.

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_head` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.NotFoundException` if the resource
            was not found.
        """
        if not self.allow_head:
            raise exceptions.MethodNotSupported(self, 'head')

        session = self._get_session(session)
        if microversion is None:
            microversion = self._get_microversion(session)
        self.microversion = microversion

        request = self._prepare_request(base_path=base_path)
        response = session.head(request.url, microversion=microversion)

        self._translate_response(response, has_body=False)

        return self

    @property
    def requires_commit(self):
        """Whether the next commit() call will do anything."""
        return (
            self._body.dirty or self._header.dirty or self.allow_empty_commit
        )

    def commit(
        self,
        session: adapter.Adapter,
        prepend_key: bool = True,
        has_body: bool = True,
        retry_on_conflict: ty.Optional[bool] = None,
        base_path: ty.Optional[str] = None,
        *,
        microversion: ty.Optional[str] = None,
        **kwargs: ty.Any,
    ) -> ty_ext.Self:
        """Commit the state of the instance to the remote resource.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param prepend_key: A boolean indicating whether the resource_key
            should be prepended in a resource update request.
            Default to True.
        :param bool retry_on_conflict: Whether to enable retries on HTTP
            CONFLICT (409). Value of ``None`` leaves the `Adapter` defaults.
        :param str base_path: Base part of the URI for modifying resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param str microversion: API version to override the negotiated one.
        :param dict kwargs: Parameters that will be passed to
            _prepare_request()

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_commit` is not set to ``True``.
        """
        if not self.allow_commit:
            raise exceptions.MethodNotSupported(self, 'commit')

        # The id cannot be dirty for an commit
        self._body._dirty.discard("id")

        # Only try to update if we actually have anything to commit.
        if not self.requires_commit:
            return self

        # Avoid providing patch unconditionally to avoid breaking subclasses
        # without it.
        if self.commit_jsonpatch:
            kwargs['patch'] = True

        request = self._prepare_request(
            prepend_key=prepend_key,
            base_path=base_path,
            **kwargs,
        )
        if microversion is None:
            microversion = self._get_microversion(session)

        return self._commit(
            session,
            request,
            self.commit_method,
            microversion,
            has_body=has_body,
            retry_on_conflict=retry_on_conflict,
        )

    def _commit(
        self,
        session,
        request,
        method,
        microversion,
        has_body=True,
        retry_on_conflict=None,
    ):
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
                f"Invalid commit method: {method}"
            )

        response = call(
            request.url,
            json=request.body,
            headers=request.headers,
            microversion=microversion,
            **kwargs,
        )

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
                raise ValueError(f"Malformed or missing path in {item}")

            try:
                component = getattr(self.__class__, field)
            except AttributeError:
                server_field = field
            else:
                server_field = component.name

            if len(parts) > 1:
                new_path = f'/{server_field}/{parts[1]}'
            else:
                new_path = f'/{server_field}'
            converted.append(dict(item, path=new_path))

        return converted

    def patch(
        self,
        session,
        patch=None,
        prepend_key=True,
        has_body=True,
        retry_on_conflict=None,
        base_path=None,
        *,
        microversion=None,
    ):
        """Patch the remote resource.

        Allows modifying the resource by providing a list of JSON patches to
        apply to it. The patches can use both the original (server-side) and
        SDK field names.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param patch: Additional JSON patch as a list or one patch item.
            If provided, it is applied on top of any changes to the current
            resource.
        :param prepend_key: A boolean indicating whether the resource_key
            should be prepended in a resource update request. Default to True.
        :param bool retry_on_conflict: Whether to enable retries on HTTP
            CONFLICT (409). Value of ``None`` leaves the `Adapter` defaults.
        :param str base_path: Base part of the URI for modifying resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param str microversion: API version to override the negotiated one.

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_patch` is not set to ``True``.
        """
        if not self.allow_patch:
            raise exceptions.MethodNotSupported(self, 'patch')

        # The id cannot be dirty for an commit
        self._body._dirty.discard("id")

        # Only try to update if we actually have anything to commit.
        if not patch and not self.requires_commit:
            return self

        request = self._prepare_request(
            prepend_key=prepend_key,
            base_path=base_path,
            patch=True,
        )
        if microversion is None:
            microversion = self._get_microversion(session)
        if patch:
            request.body += self._convert_patch(patch)

        return self._commit(
            session,
            request,
            'PATCH',
            microversion,
            has_body=has_body,
            retry_on_conflict=retry_on_conflict,
        )

    def delete(
        self,
        session: adapter.Adapter,
        error_message: ty.Optional[str] = None,
        *,
        microversion: ty.Optional[str] = None,
        **kwargs: ty.Any,
    ) -> ty_ext.Self:
        """Delete the remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param str microversion: API version to override the negotiated one.
        :param dict kwargs: Parameters that will be passed to
            _prepare_request()

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_commit` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.NotFoundException` if
            the resource was not found.
        """

        response = self._raw_delete(
            session, microversion=microversion, **kwargs
        )
        kwargs = {}
        if error_message:
            kwargs['error_message'] = error_message

        self._translate_response(
            response, has_body=False, error_message=error_message
        )
        return self

    def _raw_delete(self, session, microversion=None, **kwargs):
        if not self.allow_delete:
            raise exceptions.MethodNotSupported(self, 'delete')

        request = self._prepare_request(**kwargs)
        session = self._get_session(session)
        if microversion is None:
            microversion = self._get_microversion(session)

        return session.delete(
            request.url,
            headers=request.headers,
            microversion=microversion,
        )

    @classmethod
    def list(
        cls,
        session: adapter.Adapter,
        paginated: bool = True,
        base_path: ty.Optional[str] = None,
        allow_unknown_params: bool = False,
        *,
        microversion: ty.Optional[str] = None,
        headers: ty.Optional[dict[str, str]] = None,
        **params: ty.Any,
    ) -> ty.Generator[ty_ext.Self, None, None]:
        """This method is a generator which yields resource objects.

        This resource object list generator handles pagination and takes query
        params for response filtering.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param bool paginated: ``True`` if a GET to this resource returns
            a paginated series of responses, or ``False`` if a GET returns only
            one page of data. **When paginated is False only one page of data
            will be returned regardless of the API's support of pagination.**
        :param str base_path: Base part of the URI for listing resources, if
            different from :data:`~openstack.resource.Resource.base_path`.
        :param bool allow_unknown_params: ``True`` to accept, but discard
            unknown query parameters. This allows getting list of 'filters' and
            passing everything known to the server. ``False`` will result in
            validation exception when unknown query parameters are passed.
        :param str microversion: API version to override the negotiated one.
        :param dict headers: Additional headers to inject into the HTTP
            request.
        :param dict params: These keyword arguments are passed through the
            :meth:`~openstack.resource.QueryParamter._transpose` method
            to find if any of them match expected query parameters to be sent
            in the *params* argument to
            :meth:`~keystoneauth1.adapter.Adapter.get`. They are additionally
            checked against the :data:`~openstack.resource.Resource.base_path`
            format string to see if any path fragments need to be filled in by
            the contents of this argument.
            Parameters supported as filters by the server side are passed in
            the API call, remaining parameters are applied as filters to the
            retrieved results.

        :return: A generator of :class:`Resource` objects.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
            :data:`Resource.allow_list` is not set to ``True``.
        :raises: :exc:`~openstack.exceptions.InvalidResourceQuery` if query
            contains invalid params.
        """
        if not cls.allow_list:
            raise exceptions.MethodNotSupported(cls, 'list')

        session = cls._get_session(session)

        if microversion is None:
            microversion = cls._get_microversion(session)

        if base_path is None:
            base_path = cls.base_path

        api_filters = cls._query_mapping._validate(
            params,
            base_path=base_path,
            allow_unknown_params=True,
        )
        client_filters = {}
        # Gather query parameters which are not supported by the server
        for k, v in params.items():
            if (
                # Known attr
                hasattr(cls, k)
                # Is real attr property
                and isinstance(getattr(cls, k), fields.Body)
                # not included in the query_params
                and k not in cls._query_mapping._mapping.keys()
            ):
                client_filters[k] = v
        query_params = cls._query_mapping._transpose(api_filters, cls)
        uri = base_path % params
        uri_params = {}

        limit = query_params.get('limit')

        for k, v in params.items():
            # We need to gather URI parts to set them on the resource later
            if hasattr(cls, k) and isinstance(getattr(cls, k), fields.URI):
                uri_params[k] = v

        def _dict_filter(f, d):
            """Dict param based filtering"""
            if not d:
                return False
            for key in f.keys():
                if isinstance(f[key], dict):
                    if not _dict_filter(f[key], d.get(key, None)):
                        return False
                elif d.get(key, None) != f[key]:
                    return False
            return True

        headers_final = {"Accept": "application/json"}
        if headers:
            headers_final = {**headers_final, **headers}

        # Track the total number of resources yielded so we can paginate
        # swift objects
        total_yielded = 0
        while uri:
            # Copy query_params due to weird mock unittest interactions
            response = session.get(
                uri,
                headers=headers_final,
                params=query_params.copy(),
                microversion=microversion,
            )
            exceptions.raise_from_response(response)
            data = response.json()

            # Discard any existing pagination keys
            last_marker = query_params.pop('marker', None)
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
                # We want that URI props are available on the resource
                raw_resource.update(uri_params)

                # TODO(stephenfin): Our types say we accept a ksa Adapter, but
                # this requires an SDK Proxy. Do we update the types or rework
                # this to support use of an adapter.
                value = cls.existing(
                    microversion=microversion,
                    connection=session._get_connection(),  # type: ignore
                    **raw_resource,
                )
                marker = value.id
                filters_matched = True
                # Iterate over client filters and return only if matching
                for key in client_filters.keys():
                    if isinstance(client_filters[key], dict):
                        if not _dict_filter(
                            client_filters[key], value.get(key, None)
                        ):
                            filters_matched = False
                            break
                    elif value.get(key, None) != client_filters[key]:
                        filters_matched = False
                        break

                if filters_matched:
                    yield value
                total_yielded += 1

            if resources and paginated:
                uri, next_params = cls._get_next_link(
                    uri, response, data, marker, limit, total_yielded
                )
                try:
                    if next_params['marker'] == last_marker:
                        # If next page marker is same as what we were just
                        # asked something went terribly wrong. Some ancient
                        # services had bugs.
                        raise exceptions.SDKException(
                            'Endless pagination loop detected, aborting'
                        )
                except KeyError:
                    # do nothing, exception handling is cheaper then "if"
                    pass
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
                pagination_key = f'{cls.resources_key}_links'

            if pagination_key:
                links = data.get(pagination_key, {})
                # keystone might return a dict
                if isinstance(links, dict):
                    links = ({k: v} for k, v in links.items())

                for item in links:
                    if item.get('rel') == 'next' and 'href' in item:
                        next_link = item['href']
                        break

            # Glance has a next field in the main body
            next_link = next_link or data.get('next')
            if next_link and next_link.startswith('/v'):
                next_link = next_link[next_link.find('/', 1) :]

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
            parts = urllib.parse.urlparse(next_link)
            query_params = urllib.parse.parse_qs(parts.query)
            params.update(query_params)
            next_link = urllib.parse.urljoin(next_link, parts.path)

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
                    msg = msg % (cls.__name__, name_or_id)
                    raise exceptions.DuplicateResource(msg)

        return the_result

    @ty.overload
    @classmethod
    def find(
        cls,
        session: adapter.Adapter,
        name_or_id: str,
        ignore_missing: ty.Literal[True] = True,
        list_base_path: ty.Optional[str] = None,
        *,
        microversion: ty.Optional[str] = None,
        all_projects: ty.Optional[bool] = None,
        **params: ty.Any,
    ) -> ty.Optional[ty_ext.Self]: ...

    @ty.overload
    @classmethod
    def find(
        cls,
        session: adapter.Adapter,
        name_or_id: str,
        ignore_missing: ty.Literal[False],
        list_base_path: ty.Optional[str] = None,
        *,
        microversion: ty.Optional[str] = None,
        all_projects: ty.Optional[bool] = None,
        **params: ty.Any,
    ) -> ty_ext.Self: ...

    # excuse the duplication here: it's mypy's fault
    # https://github.com/python/mypy/issues/14764
    @ty.overload
    @classmethod
    def find(
        cls,
        session: adapter.Adapter,
        name_or_id: str,
        ignore_missing: bool,
        list_base_path: ty.Optional[str] = None,
        *,
        microversion: ty.Optional[str] = None,
        all_projects: ty.Optional[bool] = None,
        **params: ty.Any,
    ) -> ty.Optional[ty_ext.Self]: ...

    @classmethod
    def find(
        cls,
        session: adapter.Adapter,
        name_or_id: str,
        ignore_missing: bool = True,
        list_base_path: ty.Optional[str] = None,
        *,
        microversion: ty.Optional[str] = None,
        all_projects: ty.Optional[bool] = None,
        **params: ty.Any,
    ) -> ty.Optional[ty_ext.Self]:
        """Find a resource by its name or id.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param name_or_id: This resource's identifier, if needed by
            the request. The default is ``None``.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the resource does not exist.  When set to ``True``, None will
            be returned when attempting to find a nonexistent resource.
        :param str list_base_path: base_path to be used when need listing
            resources.
        :param str microversion: API version to override the negotiated one.
        :param dict params: Any additional parameters to be passed into
            underlying methods, such as to
            :meth:`~openstack.resource.Resource.existing` in order to pass on
            URI parameters.

        :return: The :class:`Resource` object matching the given name or id
            or None if nothing matches.
        :raises: :class:`openstack.exceptions.DuplicateResource` if more
            than one resource is found for this request.
        :raises: :class:`openstack.exceptions.NotFoundException` if nothing is
            found and ignore_missing is ``False``.
        """
        session = cls._get_session(session)

        # Try to short-circuit by looking directly for a matching ID.
        try:
            # TODO(stephenfin): Our types say we accept a ksa Adapter, but this
            # requires an SDK Proxy. Do we update the types or rework this to
            # support use of an adapter.
            match = cls.existing(
                id=name_or_id,
                connection=session._get_connection(),  # type: ignore
                **params,
            )
            return match.fetch(session, microversion=microversion, **params)
        except (
            exceptions.NotFoundException,
            exceptions.BadRequestException,
            exceptions.ForbiddenException,
        ):
            # NOTE(gtema): There are few places around openstack that return
            # 400 if we try to GET resource and it doesn't exist.
            pass

        if list_base_path:
            params['base_path'] = list_base_path

        # all_projects is a special case that is used by multiple services. We
        # handle it here since it doesn't make sense to pass it to the .fetch
        # call above
        if all_projects is not None:
            params['all_projects'] = all_projects

        if (
            'name' in cls._query_mapping._mapping.keys()
            and 'name' not in params
        ):
            params['name'] = name_or_id

        data = cls.list(session, **params)

        result = cls._get_one_match(name_or_id, data)
        if result is not None:
            return result

        if ignore_missing:
            return None

        raise exceptions.NotFoundException(
            f"No {cls.__name__} found for {name_or_id}"
        )


def _normalize_status(status: ty.Optional[str]) -> ty.Optional[str]:
    if status is not None:
        status = status.lower()
    return status


def wait_for_status(
    session: adapter.Adapter,
    resource: ResourceT,
    status: str,
    failures: ty.Optional[list[str]] = None,
    interval: ty.Union[int, float, None] = 2,
    wait: ty.Optional[int] = None,
    attribute: str = 'status',
    callback: ty.Optional[ty.Callable[[int], None]] = None,
) -> ResourceT:
    """Wait for the resource to be in a particular status.

    :param session: The session to use for making this request.
    :param resource: The resource to wait on to reach the status. The resource
        must have a status attribute specified via ``attribute``.
    :param status: Desired status of the resource.
    :param failures: Statuses that would indicate the transition
        failed such as 'ERROR'. Defaults to ['ERROR'].
    :param interval: Number of seconds to wait between checks. Set to ``None``
        to use the default interval.
    :param wait: Maximum number of seconds to wait for transition.
        Set to ``None`` to wait forever.
    :param attribute: Name of the resource attribute that contains the status.
    :param callback: A callback function. This will be called with a single
        value, progress. This is API specific but is generally a percentage
        value from 0-100.

    :return: The updated resource.
    :raises: :class:`~openstack.exceptions.ResourceTimeout` if the transition
        to status failed to occur in ``wait`` seconds.
    :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
        transitioned to one of the states in ``failures``.
    :raises: :class:`~AttributeError` if the resource does not have a
        ``status`` attribute
    """
    current_status = getattr(resource, attribute)
    if _normalize_status(current_status) == _normalize_status(status):
        return resource

    if failures is None:
        failures = ['ERROR']

    failures = [f.lower() for f in failures]
    name = f"{resource.__class__.__name__}:{resource.id}"
    msg = f"Timeout waiting for {name} to transition to {status}"

    for count in utils.iterate_timeout(
        timeout=wait, message=msg, wait=interval
    ):
        resource = resource.fetch(session, skip_cache=True)
        if not resource:
            raise exceptions.ResourceFailure(
                f"{name} went away while waiting for {status}"
            )

        new_status = getattr(resource, attribute)
        normalized_status = _normalize_status(new_status)
        if normalized_status == _normalize_status(status):
            return resource
        elif normalized_status in failures:
            raise exceptions.ResourceFailure(
                f"{name} transitioned to failure state {new_status}"
            )

        LOG.debug(
            'Still waiting for resource %s to reach state %s, '
            'current state is %s',
            name,
            status,
            new_status,
        )

        if callback:
            progress = getattr(resource, 'progress', None) or 0
            callback(progress)

    raise RuntimeError('cannot reach this')


def wait_for_delete(
    session: adapter.Adapter,
    resource: ResourceT,
    interval: ty.Union[int, float, None] = 2,
    wait: ty.Optional[int] = None,
    callback: ty.Optional[ty.Callable[[int], None]] = None,
) -> ResourceT:
    """Wait for a resource to be deleted.

    :param session: The session to use for making this request.
    :param resource: The resource to wait on to be deleted.
    :param interval: Number of seconds to wait between checks.
    :param wait: Maximum number of seconds to wait for the delete.
    :param callback: A callback function. This will be called with a single
        value, progress. This is API specific but is generally a percentage
        value from 0-100.

    :return: The original resource.
    :raises: :class:`~openstack.exceptions.ResourceTimeout` transition
        to status failed to occur in wait seconds.
    """
    orig_resource = resource
    for count in utils.iterate_timeout(
        timeout=wait,
        message=f"Timeout waiting for {resource.__class__.__name__}:{resource.id} to delete",
        wait=interval,
    ):
        try:
            resource = resource.fetch(session, skip_cache=True)
            if not resource:
                return orig_resource
            # Some resources like VolumeAttachment don't have status field.
            if hasattr(resource, 'status'):
                if resource.status.lower() == 'deleted':
                    return resource
        except exceptions.NotFoundException:
            return orig_resource

        if callback:
            progress = getattr(resource, 'progress', None) or 0
            callback(progress)

    raise RuntimeError('cannot reach this')
