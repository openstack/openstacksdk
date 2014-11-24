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
            try:
                value = str(self.type(value))  # validate to fail fast
            except AttributeError:
                raise TypeError('Invalid type for attr: %s' % self.name)

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

    def __init__(self, attrs=None, loaded=False):
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
        """
        return cls(kwargs, loaded=False)

    @classmethod
    def existing(cls, **kwargs):
        """Create a new instance of an existing remote resource.

        It is marked as an exact replication of a resource present on a server.
        """
        return cls(kwargs, loaded=True)

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
    def create_by_id(cls, session, attrs, r_id=None, path_args=None):
        """Create a remote resource from attributes."""
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
        if r_id:
            url = utils.urljoin(url, r_id)
            resp = session.put(url, service=cls.service, json=body).body
        else:
            resp = session.post(url, service=cls.service,
                                json=body).body

        if cls.resource_key:
            resp = resp[cls.resource_key]

        return resp

    def create(self, session):
        """Create a remote resource from this instance."""
        resp = self.create_by_id(session, self._attrs, self.id, path_args=self)
        self._attrs[self.id_attribute] = resp[self.id_attribute]
        self._reset_dirty()
        return self

    @classmethod
    def get_data_by_id(cls, session, r_id, path_args=None,
                       include_headers=False):
        """Get a remote resource from an id as attributes."""
        if not cls.allow_retrieve:
            raise exceptions.MethodNotSupported('retrieve')

        if path_args:
            url = cls.base_path % path_args
        else:
            url = cls.base_path
        url = utils.urljoin(url, r_id)
        response = session.get(url, service=cls.service)
        body = response.body

        if cls.resource_key:
            body = body[cls.resource_key]

        if include_headers:
            body.update(response.headers)

        return body

    @classmethod
    def get_by_id(cls, session, r_id, path_args=None, include_headers=False):
        """Get a remote resource from an id as an object."""
        body = cls.get_data_by_id(session, r_id, path_args=path_args,
                                  include_headers=include_headers)
        return cls.existing(**body)

    def get(self, session, include_headers=False):
        """Get the remote resource associated with this class."""
        body = self.get_data_by_id(session, self.id, path_args=self,
                                   include_headers=include_headers)
        self._attrs.update(body)
        self._loaded = True
        return self

    @classmethod
    def head_data_by_id(cls, session, r_id, path_args=None):
        """Get remote resource headers from an id as attributes."""
        if not cls.allow_head:
            raise exceptions.MethodNotSupported('head')

        if path_args:
            url = cls.base_path % path_args
        else:
            url = cls.base_path
        url = utils.urljoin(url, r_id)

        data = session.head(url, service=cls.service, accept=None).headers

        return data

    @classmethod
    def head_by_id(cls, session, r_id, path_args=None):
        """Get remote resource headers from an id as an object."""
        data = cls.head_data_by_id(session, r_id, path_args=path_args)
        return cls.existing(**data)

    def head(self, session):
        """Get the remote resource headers associated with this class."""
        data = self.head_data_by_id(session, self.id, path_args=self)
        self._attrs.update(data)
        self._loaded = True
        return self

    @classmethod
    def update_by_id(cls, session, r_id, attrs, path_args=None):
        """Update a remote resource with the given attributes."""
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
        url = utils.urljoin(url, r_id)
        resp = session.patch(url, service=cls.service, json=body).body

        if cls.resource_key:
            resp = resp[cls.resource_key]

        return resp

    def update(self, session):
        """Update the remote resource associated with this instance."""
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
    def delete_by_id(cls, session, r_id, path_args=None):
        """Delete a remote resource associated with the given id."""
        if not cls.allow_delete:
            raise exceptions.MethodNotSupported('delete')

        if path_args:
            url = cls.base_path % path_args
        else:
            url = cls.base_path
        url = utils.urljoin(url, r_id)
        session.delete(url, service=cls.service, accept=None)

    def delete(self, session):
        """Delete the remote resource associated with this instance."""
        self.delete_by_id(session, self.id, path_args=self)

    @classmethod
    def list(cls, session, limit=None, marker=None, path_args=None, **params):
        """Return a generator that will page through results of GET requests.

        This method starts at `limit` and `marker` (both defaulting to None),
        advances the marker to the last item received, and continues paging
        until no results are returned.
        """
        if not cls.allow_list:
            raise exceptions.MethodNotSupported('list')

        more_data = True

        while more_data:
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

            # TODO(briancurtin): Although there are a few different ways
            # across services, we can know from a response if it's the end
            # without doing an extra request to get an empty response.
            # Resources should probably carry something like a `_should_page`
            # method to handle their service's pagination style.
            if not resp:
                more_data = False

            for data in resp:
                value = cls.existing(**data)
                marker = value.id
                yield value

    @classmethod
    def find(cls, session, name_or_id, path_args=None):
        """Find a resource by name or id as an instance."""
        try:
            args = {
                cls.id_attribute: name_or_id,
                'fields': cls.id_attribute,
                'path_args': path_args,
            }
            info = cls.list(session, **args)
            # If there is exactly one result available, return it.
            result = None
            try:
                result = next(info)
                next(info)
            except StopIteration:
                if result is not None:
                    return result
        except exceptions.HttpException:
            pass

        if cls.name_attribute:
            params = {cls.name_attribute: name_or_id,
                      'fields': cls.id_attribute}
            info = cls.list(session, path_args=path_args, **params)
            result = None
            # Take the first value as our result. If another value is,
            # available then raise DuplicateResource.
            try:
                result = next(info)
                next(info)
                msg = "More than one %s exists with the name '%s'."
                msg = (msg % (cls.get_resource_name(), name_or_id))
                raise exceptions.DuplicateResource(msg)
            except StopIteration:
                # We got here because `info` either gave us the result
                # or it was empty.
                if result is not None:
                    return result

        msg = ("No %s with a name or ID of '%s' exists." %
               (cls.get_resource_name(), name_or_id))
        raise exceptions.ResourceNotFound(msg)
