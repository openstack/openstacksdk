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

import six
from six.moves.urllib import parse as url_parse

from openstack import exceptions
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
            value = instance._attrs[self.name]
        except KeyError:
            try:
                value = instance._attrs[self.alias]
            except KeyError:
                return self.default

        if self.type and not isinstance(value, self.type):
            value = self.type(value)
            attr = getattr(value, 'parsed', None)
            if attr is not None:
                value = attr

        return value

    def __set__(self, instance, value):
        if self.type and not isinstance(value, self.type):
            value = str(self.type(value))  # validate to fail fast

        instance._attrs[self.name] = value

    def __delete__(self, instance):
        try:
            del instance._attrs[self.name]
        except KeyError:
            try:
                del instance._attrs[self.alias]
            except KeyError:
                pass


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

    put_update = False

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
        if attrs is None:
            attrs = {}

        self._attrs = attrs
        # ensure setters are called for type coercion
        for k, v in attrs.items():
            if k != 'id':  # id property is read only
                setattr(self, k, v)

        self._dirty = set() if loaded else set(attrs.keys())
        self._loaded = loaded

    def __repr__(self):
        return "%s: %s" % (self.get_resource_name(), self._attrs)

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
    def from_id(cls, value):
        """Create an instance from an ID or return an existing instance.

        Instance creation is done via cls.new.
        """
        # This method is useful in the higher level, in cases where operations
        # need to depend on having Resource objects, but the API is flexible
        # in taking text values which represent those objects.
        if isinstance(value, cls):
            return value
        elif isinstance(value, six.string_types):
            return cls.new(**{cls.id_attribute: value})
        else:
            raise ValueError("value must be %s instance or id" % cls.__name__)

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
    def is_dirty(self):
        """True if the resource needs to be updated to the remote."""
        return len(self._dirty) > 0

    def _reset_dirty(self):
        self._dirty = set()

    ##
    # CRUD OPERATIONS
    ##

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
            raise exceptions.MethodNotSupported('create')

        if cls.resource_key:
            body = {cls.resource_key: attrs}
        else:
            body = attrs

        if path_args:
            url = cls.base_path % path_args
        else:
            url = cls.base_path
        if resource_id:
            url = utils.urljoin(url, resource_id)
            resp = session.put(url, service=cls.service, json=body).body
        else:
            resp = session.post(url, service=cls.service,
                                json=body).body

        if cls.resource_key:
            resp = resp[cls.resource_key]

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
        self._attrs[self.id_attribute] = resp[self.id_attribute]
        self._reset_dirty()
        return self

    @classmethod
    def get_data_by_id(cls, session, resource_id, path_args=None,
                       include_headers=False):
        """Get a the attributes of a remote resource from an id.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request. The default is ``None``.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.
        :param bool include_headers: ``True`` if header data should be
                                     included in the response body,
                                     ``False`` if not.

        :return: A ``dict`` representing the response body.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_retrieve` is not set to ``True``.
        """
        if not cls.allow_retrieve:
            raise exceptions.MethodNotSupported('retrieve')

        if path_args:
            url = cls.base_path % path_args
        else:
            url = cls.base_path
        url = utils.urljoin(url, resource_id)
        response = session.get(url, service=cls.service)
        body = response.body

        if cls.resource_key:
            body = body[cls.resource_key]

        if include_headers:
            body.update(response.headers)

        return body

    @classmethod
    def get_by_id(cls, session, resource_id, path_args=None,
                  include_headers=False):
        """Get an object representing a remote resource from an id.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request. The default is ``None``.
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

    def get(self, session, include_headers=False):
        """Get the remote resource associated with this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_retrieve` is not set to ``True``.
        """
        body = self.get_data_by_id(session, self.id, path_args=self,
                                   include_headers=include_headers)
        self._attrs.update(body)
        self._loaded = True
        return self

    @classmethod
    def head_data_by_id(cls, session, resource_id, path_args=None):
        """Get a dictionary representing the headers of a remote resource.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request. The default is ``None``.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.

        :return: A ``dict`` representing the headers.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_head` is not set to ``True``.
        """
        if not cls.allow_head:
            raise exceptions.MethodNotSupported('head')

        if path_args:
            url = cls.base_path % path_args
        else:
            url = cls.base_path
        url = utils.urljoin(url, resource_id)

        data = session.head(url, service=cls.service, accept=None).headers

        return data

    @classmethod
    def head_by_id(cls, session, resource_id, path_args=None):
        """Get an object representing the headers of a remote resource.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request. The default is ``None``.
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
                            the request. The default is ``None``.
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
            raise exceptions.MethodNotSupported('update')

        if cls.resource_key:
            body = {cls.resource_key: attrs}
        else:
            body = attrs

        if path_args:
            url = cls.base_path % path_args
        else:
            url = cls.base_path
        url = utils.urljoin(url, resource_id)
        if cls.put_update:
            resp = session.put(url, service=cls.service, json=body).body
        else:
            resp = session.patch(url, service=cls.service, json=body).body

        if cls.resource_key:
            resp = resp[cls.resource_key]

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

        self._reset_dirty()
        return self

    @classmethod
    def delete_by_id(cls, session, resource_id, path_args=None):
        """Delete a remote resource with the given id.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request. The default is ``None``.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.

        :return: ``None``
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_delete` is not set to ``True``.
        """
        if not cls.allow_delete:
            raise exceptions.MethodNotSupported('delete')

        if path_args:
            url = cls.base_path % path_args
        else:
            url = cls.base_path
        url = utils.urljoin(url, resource_id)
        session.delete(url, service=cls.service, accept=None)

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
    def list(cls, session, limit=None, marker=None, path_args=None, **params):
        """Get a response that is a list of potentially paginated objects.

        This method starts at ``limit`` and ``marker`` (both defaulting to
        None), advances the marker to the last item received in each response,
        and continues making requests for more resources until no results
        are returned.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param limit: The maximum amount of results to retrieve.
                      The default is ``None``, which means no limit will be
                      set, and the underlying API will return its default
                      amount of responses.
        :param marker: The position in the list to begin requests from.
                       The type of value to use for ``marker`` depends on
                       the API being called.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.
        :param dict params: Parameters to be passed into the underlying
                            :meth:`~openstack.session.Session.get` method.

        :return: A generator of :class:`Resource` objects.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_list` is not set to ``True``.
        """
        if not cls.allow_list:
            raise exceptions.MethodNotSupported('list')

        more_data = True

        while more_data:
            resp = cls.page(session, limit, marker, path_args, **params)

            # TODO(briancurtin): Although there are a few different ways
            # across services, we can know from a response if it's the end
            # without doing an extra request to get an empty response.
            # Resources should probably carry something like a `_should_page`
            # method to handle their service's pagination style.
            if not resp:
                more_data = False

            # Keep track of how many items we've yielded. If we yielded
            # less than our limit, we don't need to do an extra request
            # to get back an empty data set, which acts as a sentinel.
            yielded = 0
            for data in resp:
                value = cls.existing(**data)
                marker = value.id
                yielded += 1
                yield value

            if limit and yielded < limit:
                more_data = False

    @classmethod
    def page(cls, session, limit, marker=None, path_args=None, **params):
        """Get a one page response.

        This method gets starting at ``marker`` with a maximum of ``limit``
        records.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param limit: The maximum amount of results to retrieve.
        :param marker: The position in the list to begin requests from.
                       The type of value to use for ``marker`` depends on
                       the API being called.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.
        :param dict params: Parameters to be passed into the underlying
                            :meth:`~openstack.session.Session.get` method.

        :return: An array of :class:`Resource` objects.
        """

        filters = {}

        if limit:
            filters['limit'] = limit
        if marker:
            filters['marker'] = marker

        if path_args:
            url = cls.base_path % path_args
        else:
            url = cls.base_path
        if filters:
            url = '%s?%s' % (url, url_parse.urlencode(filters))

        resp = session.get(url, service=cls.service, params=params).body

        if cls.resources_key:
            resp = resp[cls.resources_key]

        return resp

    @classmethod
    def find(cls, session, name_or_id, path_args=None):
        """Find a resource by its name or id.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param resource_id: This resource's identifier, if needed by
                            the request. The default is ``None``.
        :param dict path_args: A dictionary of arguments to construct
                               a compound URL.
                               See `How path_args are used`_ for details.

        :return: The :class:`Resource` object matching the given name or id
                 or None if nothing matches.
        """
        try:
            args = {
                cls.id_attribute: name_or_id,
                'fields': cls.id_attribute,
                'path_args': path_args,
            }
            info = cls.page(session, limit=2, **args)
            if len(info) == 1:
                return cls.existing(**info[0])
        except exceptions.HttpException:
            pass

        if cls.name_attribute:
            params = {cls.name_attribute: name_or_id,
                      'fields': cls.id_attribute}
            info = cls.page(session, limit=2, path_args=path_args, **params)
            if len(info) == 1:
                return cls.existing(**info[0])
            if len(info) > 1:
                msg = "More than one %s exists with the name '%s'."
                msg = (msg % (cls.get_resource_name(), name_or_id))
                raise exceptions.DuplicateResource(msg)

        return None
