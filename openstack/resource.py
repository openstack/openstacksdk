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
class that represent a remote resource.  Attributes of the resource
are defined by the responses from the server rather than in code so
that we don't have to try and keep up with all possible attributes
and extensions. This may be changed in the future.

The :class:`~openstack.resource.prop` class is a helper for
definiting properties in a resource.

For update management, :class:`~openstack.resource.Resource`
maintains a dirty list so when updating an object only the attributes
that have actually been changed are sent to the server.

There is also some support here for lazy loading that needs improvement.

There are plenty of examples of use of this class in the SDK code.
"""

import abc
import collections
import copy
import itertools
import time

import six
from six.moves.urllib import parse as url_parse

from openstack import exceptions
from openstack import format
from openstack import utils


class prop(object):
    """A helper for defining properties in a resource.

    A prop defines some known attributes within a resource's values.
    For example we know a User resource will have a name:

        >>> class User(Resource):
        ...     name = prop('name')
        ...
        >>> u = User()
        >>> u.name = 'John Doe'
        >>> print u['name']
        John Doe

    User objects can now be accessed via the User().name attribute. The 'name'
    value we pass as an attribute is the name of the attribute in the message.
    This means that you don't need to use the same name for your attribute as
    will be set within the object. For example:

        >>> class User(Resource):
        ...     name = prop('userName')
        ...
        >>> u = User()
        >>> u.name = 'John Doe'
        >>> print u['userName']
        John Doe

    There is limited validation ability in props.

    You can validate the type of values that are set:

        >>> class User(Resource):
        ...     name = prop('userName')
        ...     age = prop('age', type=int)
        ...
        >>> u = User()
        >>> u.age = 'thirty'
        TypeError: Invalid type for attr age


    By specifying an alias attribute name, that alias will be read when the
    primary attribute name does not appear within the resource:

        >>> class User(Resource):
        ...     name = prop('address', alias='location')
        ...
        >>> u = User(location='Far Away')
        >>> print u['address']
        Far Away
    """

    def __init__(self, name, alias=None, type=None, default=None):
        self.name = name
        self.type = type
        self.alias = alias
        self.default = default

    def __get__(self, instance, owner):
        if instance is None:
            return None
        try:
            value = instance[self.name]
            # self.type() should not be called on None objects.
            if value is None:
                return None
        except KeyError:
            try:
                value = instance[self.alias]
            except (KeyError, AttributeError):
                # If we either don't find the key or we don't have an alias
                return self.default

        if self.type and not isinstance(value, self.type):
            if issubclass(self.type, Resource):
                if isinstance(value, six.string_types):
                    value = self.type({self.type.id_attribute: value})
                else:
                    value = self.type(value)
            elif issubclass(self.type, format.Formatter):
                value = self.type.deserialize(value)
            else:
                value = self.type(value)

        return value

    def __set__(self, instance, value):
        if (self.type and not isinstance(value, self.type) and
                value != self.default):
            if issubclass(self.type, Resource):
                if isinstance(value, six.string_types):
                    value = self.type({self.type.id_attribute: value})
                else:
                    value = self.type(value)
            elif issubclass(self.type, format.Formatter):
                value = self.type.serialize(value)
            else:
                value = str(self.type(value))  # validate to fail fast

        # If we already have a value set for the alias name, pop it out
        # and store the real name instead. This happens when the alias
        # has the same name as this prop is named.
        if self.alias in instance._attrs:
            instance._attrs.pop(self.alias)

        instance[self.name] = value

    def __delete__(self, instance):
        try:
            del instance[self.name]
        except KeyError:
            try:
                del instance[self.alias]
            except KeyError:
                pass


#: Key in attributes for header properties
HEADERS = 'headers'


class header(prop):
    """A helper for defining header properties in a resource.

    This property should be used for values passed in the header of a resource.
    Header values are stored in a special 'headers' attribute of a resource.
    Using this property will make it easier for users to access those values.
    For example, and object store container:

        >>> class Container(Resource):
        ...     name = prop("name")
        ...     object_count = header("x-container-object-count")
        ...
        >>> c = Container({name='pix'})
        >>> c.head(session)
        >>> print c["headers"]["x-container-object-count"]
        4
        >>> print c.object_count
        4

    The first print shows accessing the header value without the property
    and the second print shows accessing the header with the property helper.
    """

    def _get_headers(self, instance):
        if instance is None:
            return None
        if HEADERS in instance:
            return instance[HEADERS]
        return None

    def __get__(self, instance, owner):
        headers = self._get_headers(instance)
        return super(header, self).__get__(headers, owner)

    def __set__(self, instance, value):
        headers = self._get_headers(instance)
        if headers is None:
            headers = instance._attrs[HEADERS] = {}
        headers[self.name] = value
        instance.set_headers(headers)


@six.add_metaclass(abc.ABCMeta)
class Resource(collections.MutableMapping):

    #: Singular form of key for resource.
    resource_key = None
    #: Common name for resource.
    resource_name = None
    #: Plural form of key for resource.
    resources_key = None

    #: Attribute key associated with the id for this resource.
    id_attribute = 'id'
    #: Attribute key associated with the name for this resource.
    name_attribute = 'name'
    #: Attribute key associated with 'location' from response headers
    location = header('location')

    #: The base part of the url for this resource.
    base_path = ''

    #: The service associated with this resource to find the service URL.
    service = None

    #: Allow create operation for this resource.
    allow_create = False
    #: Allow retrieve/get operation for this resource.
    allow_retrieve = False
    #: Allow update operation for this resource.
    allow_update = False
    #: Allow delete operation for this resource.
    allow_delete = False
    #: Allow list operation for this resource.
    allow_list = False
    #: Allow head operation for this resource.
    allow_head = False

    patch_update = False

    def __init__(self, attrs=None, loaded=False):
        """Construct a Resource to interact with a service's REST API.

        The Resource class offers two class methods to construct
        resource objects, which are preferrable to entering through
        this initializer. See :meth:`Resource.new` and
        :meth:`Resource.existing`.

        :param dict attrs: The attributes to set when constructing
                           this Resource.
        :param bool loaded: ``True`` if this Resource exists on
                            the server, ``False`` if it does not.
        """
        self._attrs = {} if attrs is None else attrs.copy()
        self._dirty = set() if loaded else set(self._attrs.keys())
        self.update_attrs(self._attrs)
        self._loaded = loaded

    def __repr__(self):
        return "%s.%s(attrs=%s, loaded=%s)" % (self.__module__,
                                               self.__class__.__name__,
                                               self._attrs, self._loaded)

    @classmethod
    def get_resource_name(cls):
        if cls.resource_name:
            return cls.resource_name
        if cls.resource_key:
            return cls.resource_key
        return cls().__class__.__name__

    ##
    # CONSTRUCTORS
    ##

    @classmethod
    def new(cls, **kwargs):
        """Create a new instance of this resource.

        Internally set flags such that it is marked as not present on the
        server.

        :param dict kwargs: Each of the named arguments will be set as
                            attributes on the resulting Resource object.
        """
        return cls(kwargs, loaded=False)

    @classmethod
    def existing(cls, **kwargs):
        """Create an instance of an existing remote resource.

        It is marked as an exact replication of a resource present on a server.

        :param dict kwargs: Each of the named arguments will be set as
                            attributes on the resulting Resource object.
        """
        return cls(kwargs, loaded=True)

    @classmethod
    def _from_attr(cls, attribute, value):
        # This method is useful in the higher level, in cases where operations
        # need to depend on having Resource objects, but the API is flexible
        # in taking text values which represent those objects.
        if isinstance(value, cls):
            return value
        elif isinstance(value, six.string_types):
            return cls.new(**{attribute: value})
        else:
            raise ValueError("value must be %s instance or %s" % (
                cls.__name__, attribute))

    @classmethod
    def from_id(cls, value):
        """Create an instance from an ID or return an existing instance.

        New instances are created with :meth:`~openstack.resource.Resource.new`

        :param value: If ``value`` is an instance of this Resource type,
                      it is returned.
                      If ``value`` is an ID which an instance of this
                      Resource type can be created with, one is created
                      and returned.

        :rtype: :class:`~openstack.resource.Resource` or the
                appropriate subclass.
        :raises: :exc:`ValueError` if ``value`` is not an instance of
                 this Resource type or a valid ``id``.
        """
        return cls._from_attr(cls.id_attribute, value)

    @classmethod
    def from_name(cls, value):
        """Create an instance from a name or return an existing instance.

        New instances are created with :meth:`~openstack.resource.Resource.new`

        :param value: If ``value`` is an instance of this Resource type,
                      it is returned.
                      If ``value`` is a name which an instance of this
                      Resource type can be created with, one is created
                      and returned.

        :rtype: :class:`~openstack.resource.Resource` or the
                appropriate subclass.
        :raises: :exc:`ValueError` if ``value`` is not an instance of
                this Resource type or a valid ``name``.
        """
        return cls._from_attr(cls.name_attribute, value)

    ##
    # MUTABLE MAPPING IMPLEMENTATION
    ##

    def __getitem__(self, name):
        return self._attrs[name]

    def __setitem__(self, name, value):
        try:
            orig = self._attrs[name]
        except KeyError:
            changed = True
        else:
            changed = orig != value

        if changed:
            self._attrs[name] = value
            self._dirty.add(name)

    def __delitem__(self, name):
        del self._attrs[name]
        self._dirty.add(name)

    def __len__(self):
        return len(self._attrs)

    def __iter__(self):
        return iter(self._attrs)

    ##
    # BASE PROPERTIES/OPERATIONS
    ##

    @property
    def id(self):
        """The identifier associated with this resource.

        The true value of the ``id`` property comes from the
        attribute set as :data:`id_attribute`. For example,
        a container's name may be the appropirate identifier,
        so ``id_attribute = "name"`` would be set on the
        :class:`Resource`, and ``Resource.name`` would be
        conveniently accessible through ``id``.
        """
        return self._attrs.get(self.id_attribute, None)

    @id.deleter
    def id(self):
        del self._attrs[self.id_attribute]

    @property
    def name(self):
        """The name associated with this resource.

        The true value of the ``name`` property comes from the
        attribute set as :data:`name_attribute`.
        """
        return self._attrs.get(self.name_attribute, None)

    @name.setter
    def name(self, value):
        self._attrs[self.name_attribute] = value

    @name.deleter
    def name(self):
        del self._attrs[self.name_attribute]

    @property
    def is_dirty(self):
        """True if the resource needs to be updated to the remote."""
        return len(self._dirty) > 0

    def _reset_dirty(self):
        self._dirty = set()

    def _update_attrs_from_response(self, resp, include_headers=False):
        resp_headers = resp.pop(HEADERS, None)
        self._attrs.update(resp)
        self.update_attrs(self._attrs)
        if include_headers and (resp_headers is not None):
            self.set_headers(resp_headers)

    def update_attrs(self, *args, **kwargs):
        """Update the attributes on this resource

        Note that this is implemented because Resource.update overrides
        the update method we would get from the MutableMapping base class.

        :params args: A dictionary of attributes to be updated.
        :params kwargs: Named arguments to be set on this instance.
                        When a key corresponds to a resource.prop,
                        it will be set via resource.prop.__set__.

        :rtype: None
        """
        ignore_none = kwargs.pop("ignore_none", False)

        # ensure setters are called for type coercion
        for key, value in itertools.chain(dict(*args).items(), kwargs.items()):
            if key != self.id_attribute:  # id property is read only

                # Don't allow None values to override a key unless we've
                # explicitly specified they can. Proxy methods have default
                # None arguments that we don't want to override any values
                # that may have been passed in on Resource instances.
                if not all([ignore_none, value is None]):
                    if key != "id":
                        setattr(self, key, value)
                    self[key] = value

    def get_headers(self):
        if HEADERS in self._attrs:
            return self._attrs[HEADERS]
        return {}

    def set_headers(self, values):
        self._attrs[HEADERS] = values
        self._dirty.add(HEADERS)

    def to_dict(self):
        attrs = copy.deepcopy(self._attrs)
        headers = attrs.pop(HEADERS, {})
        attrs.update(headers)
        return attrs

    ##
    # CRUD OPERATIONS
    ##

    @staticmethod
    def get_id(value):
        """If a value is a Resource, return the canonical ID."""
        if isinstance(value, Resource):
            return value.id
        else:
            return value

    @staticmethod
    def convert_ids(attrs):
        """Return an attribute dictionary suitable for create/update

        As some attributes may be Resource types, their ``id`` attribute
        needs to be put in the Resource instance's place in order
        to be properly serialized and understood by the server.
        """
        if attrs is None:
            return

        converted = attrs.copy()
        for key, value in converted.items():
            if isinstance(value, Resource):
                converted[key] = value.id

        return converted

    @classmethod
    def _get_create_body(cls, attrs):
        if cls.resource_key:
            return {cls.resource_key: attrs}
        else:
            return attrs

    @classmethod
    def _get_url(cls, path_args=None, resource_id=None):
        if path_args:
            url = cls.base_path % path_args
        else:
            url = cls.base_path
        if resource_id is not None:
            url = utils.urljoin(url, resource_id)
        return url

    @classmethod
    def create_by_id(cls, session, attrs, resource_id=None, path_args=None):
        """Create a remote resource from its attributes.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param dict attrs: The attributes to be sent in the body
                           of the request.
        :param resource_id: This resource's identifier, if needed by
                            the request. The default is ``None``.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.

        :return: A ``dict`` representing the response body.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_create` is not set to ``True``.
        """
        if not cls.allow_create:
            raise exceptions.MethodNotSupported(cls, 'create')

        # Convert attributes from Resource types into their ids.
        attrs = cls.convert_ids(attrs)
        headers = attrs.pop(HEADERS, None)

        body = cls._get_create_body(attrs)

        url = cls._get_url(path_args, resource_id)
        args = {'json': body}
        if headers:
            args[HEADERS] = headers
        if resource_id:
            resp = session.put(url, endpoint_filter=cls.service, **args)
        else:
            resp = session.post(url, endpoint_filter=cls.service, **args)
        resp_headers = resp.headers
        resp = resp.json()

        if cls.resource_key:
            resp = resp[cls.resource_key]
        if resp_headers:
            resp[HEADERS] = copy.deepcopy(resp_headers)

        return resp

    def create(self, session):
        """Create a remote resource from this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_create` is not set to ``True``.
        """
        resp = self.create_by_id(session, self._attrs, self.id, path_args=self)
        self._update_attrs_from_response(resp, include_headers=True)
        self._reset_dirty()
        return self

    @classmethod
    def get_data_by_id(cls, session, resource_id, path_args=None, args=None,
                       include_headers=False):
        """Get the attributes of a remote resource from an id.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.
        :param dict args: A dictionary of query parameters to be appended to
                          the compound URL.
        :param bool include_headers: ``True`` if header data should be
                                     included in the response body,
                                     ``False`` if not.

        :return: A ``dict`` representing the response body.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_retrieve` is not set to ``True``.
        """
        if not cls.allow_retrieve:
            raise exceptions.MethodNotSupported(cls, 'retrieve')

        url = cls._get_url(path_args, resource_id)
        if args:
            url = '?'.join([url, url_parse.urlencode(args)])
        response = session.get(url, endpoint_filter=cls.service)
        body = response.json()

        if cls.resource_key:
            body = body[cls.resource_key]

        if include_headers:
            body[HEADERS] = response.headers

        return body

    @classmethod
    def get_by_id(cls, session, resource_id, path_args=None,
                  include_headers=False):
        """Get an object representing a remote resource from an id.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.
        :param bool include_headers: ``True`` if header data should be
                                     included in the response body,
                                     ``False`` if not.

        :return: A :class:`Resource` object representing the
                 response body.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_retrieve` is not set to ``True``.
        """
        body = cls.get_data_by_id(session, resource_id, path_args=path_args,
                                  include_headers=include_headers)
        return cls.existing(**body)

    def get(self, session, include_headers=False, args=None):
        """Get the remote resource associated with this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param bool include_headers: ``True`` if header data should be
                                     included in the response body,
                                     ``False`` if not.
        :param dict args: A dictionary of query parameters to be appended to
                          the compound URL.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_retrieve` is not set to ``True``.
        """
        body = self.get_data_by_id(session, self.id, path_args=self, args=args,
                                   include_headers=include_headers)
        self._update_attrs_from_response(body, include_headers)
        self._loaded = True
        return self

    @classmethod
    def head_data_by_id(cls, session, resource_id, path_args=None):
        """Get a dictionary representing the headers of a remote resource.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.

        :return: A ``dict`` containing the headers.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_head` is not set to ``True``.
        """
        if not cls.allow_head:
            raise exceptions.MethodNotSupported(cls, 'head')

        url = cls._get_url(path_args, resource_id)

        headers = {'Accept': ''}
        resp = session.head(url, endpoint_filter=cls.service, headers=headers)

        return {HEADERS: resp.headers}

    @classmethod
    def head_by_id(cls, session, resource_id, path_args=None):
        """Get an object representing the headers of a remote resource.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.

        :return: A :class:`Resource` representing the headers.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_head` is not set to ``True``.
        """
        data = cls.head_data_by_id(session, resource_id, path_args=path_args)
        return cls.existing(**data)

    def head(self, session):
        """Get the remote resource headers associated with this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_head` is not set to ``True``.
        """
        data = self.head_data_by_id(session, self.id, path_args=self)
        self._attrs.update(data)
        self._loaded = True
        return self

    @classmethod
    def update_by_id(cls, session, resource_id, attrs, path_args=None):
        """Update a remote resource with the given attributes.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request.
        :param dict attrs: The attributes to be sent in the body
                           of the request.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.

        :return: A ``dict`` representing the response body.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_update` is not set to ``True``.
        """
        if not cls.allow_update:
            raise exceptions.MethodNotSupported(cls, 'update')

        # Convert attributes from Resource types into their ids.
        attrs = cls.convert_ids(attrs)
        if attrs and cls.id_attribute in attrs:
            del attrs[cls.id_attribute]
        headers = attrs.pop(HEADERS, None)

        if cls.resource_key:
            body = {cls.resource_key: attrs}
        else:
            body = attrs

        url = cls._get_url(path_args, resource_id)
        args = {'json': body}
        if headers:
            args[HEADERS] = headers
        if cls.patch_update:
            resp = session.patch(url, endpoint_filter=cls.service, **args)
        else:
            resp = session.put(url, endpoint_filter=cls.service, **args)
        resp_headers = resp.headers
        resp = resp.json()

        if cls.resource_key and cls.resource_key in resp.keys():
            resp = resp[cls.resource_key]
        if resp_headers:
            resp[HEADERS] = resp_headers

        return resp

    def update(self, session):
        """Update the remote resource associated with this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_update` is not set to ``True``.
        """
        if not self.is_dirty:
            return

        dirty_attrs = dict((k, self._attrs[k]) for k in self._dirty)
        resp = self.update_by_id(session, self.id, dirty_attrs, path_args=self)

        try:
            resp_id = resp.pop(self.id_attribute)
        except KeyError:
            pass
        else:
            assert resp_id == self.id
        self._update_attrs_from_response(resp, include_headers=True)
        self._reset_dirty()
        return self

    @classmethod
    def delete_by_id(cls, session, resource_id, path_args=None):
        """Delete a remote resource with the given id.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.

        :return: ``None``
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_delete` is not set to ``True``.
        """
        if not cls.allow_delete:
            raise exceptions.MethodNotSupported(cls, 'delete')

        url = cls._get_url(path_args, resource_id)
        headers = {'Accept': ''}
        session.delete(url, endpoint_filter=cls.service, headers=headers)

    def delete(self, session):
        """Delete the remote resource associated with this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: ``None``
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_update` is not set to ``True``.
        """
        self.delete_by_id(session, self.id, path_args=self)

    @classmethod
    def list(cls, session, path_args=None, paginated=False, params=None):
        """This method is a generator which yields resource objects.

        This resource object list generator handles pagination and takes query
        params for response filtering.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.
        :param bool paginated: ``True`` if a GET to this resource returns
                               a paginated series of responses, or ``False``
                               if a GET returns only one page of data.
                               **When paginated is False only one
                               page of data will be returned regardless
                               of the API's support of pagination.**
        :param dict params: Query parameters to be passed into the underlying
                            :meth:`~openstack.session.Session.get` method.
                            Values that the server may support include `limit`
                            and `marker`.

        :return: A generator of :class:`Resource` objects.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_list` is not set to ``True``.
        """
        if not cls.allow_list:
            raise exceptions.MethodNotSupported(cls, 'list')

        more_data = True
        params = {} if params is None else params
        url = cls._get_url(path_args)
        headers = {'Accept': 'application/json'}
        while more_data:
            resp = session.get(url, endpoint_filter=cls.service,
                               headers=headers, params=params)
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
            if 'limit' in params and yielded < params['limit']:
                return
            params['limit'] = yielded
            params['marker'] = new_marker

    @classmethod
    def find(cls, session, name_or_id, path_args=None, ignore_missing=True):
        """Find a resource by its name or id.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param name_or_id: This resource's identifier, if needed by
                           the request. The default is ``None``.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.

        :return: The :class:`Resource` object matching the given name or id
                 or None if nothing matches.
        :raises: :class:`openstack.exceptions.DuplicateResource` if more
                 than one resource is found for this request.
        :raises: :class:`openstack.exceptions.ResourceNotFound` if nothing
                 is found and ignore_missing is ``False``.
        """
        # Only return one matching resource.
        def get_one_match(results, the_id, the_name):
            the_result = None
            for item in results:
                maybe_result = cls.existing(**item)

                id_value, name_value = None, None
                if the_id is not None:
                    id_value = getattr(maybe_result, the_id, None)
                if the_name is not None:
                    name_value = getattr(maybe_result, the_name, None)

                if (id_value == name_or_id) or (name_value == name_or_id):
                    # Only allow one resource to be found. If we already
                    # found a match, raise an exception to show it.
                    if the_result is None:
                        the_result = maybe_result
                    else:
                        msg = "More than one %s exists with the name '%s'."
                        msg = (msg % (cls.get_resource_name(), name_or_id))
                        raise exceptions.DuplicateResource(msg)

            return the_result

        # Try to short-circuit by looking directly for a matching ID.
        try:
            if cls.allow_retrieve:
                return cls.get_by_id(session, name_or_id, path_args=path_args)
        except exceptions.NotFoundException:
            pass

        data = cls.list(session, path_args=path_args)

        result = get_one_match(data, cls.id_attribute, cls.name_attribute)
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
