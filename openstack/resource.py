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

import abc
import collections

import six
from six.moves.urllib import parse as url_parse

from openstack import utils


class MethodNotSupported(Exception):
    """The resource does not support this operation type."""


class prop(object):
    """A helper for defining properties on a Resource.

    A Resource.prop defines some known attributes within a resource's values.
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
    """

    def __init__(self, name, type=None):
        self.name = name
        self.type = type

    def __get__(self, instance, owner):
        try:
            return instance._attrs[self.name]
        except KeyError:
            raise AttributeError('Unset property: %s', self.name)

    def __set__(self, instance, value):
        if self.type and not isinstance(value, self.type):
            raise TypeError('Invalid type for attr %s' % self.name)

        instance._attrs[self.name] = value

    def __delete__(self, instance):
        try:
            del instance._attrs[self.name]
        except KeyError:
            raise AttributeError('Unset property: %s', self.name)


@six.add_metaclass(abc.ABCMeta)
class Resource(collections.MutableMapping):
    """A base class that represents a remote resource.

    Attributes of the resource are defined by the responses from the server
    rather than in code so that we don't have to try and keep up with all
    possible attributes and extensions. This may be changed in the future.

    For update management we maintain a dirty list so when updating an object
    only the attributes that have actually been changed are sent to the server.

    There is some support here for lazy loading that needs improvement.
    """

    # the singular and plural forms of the key element
    resource_key = None
    resources_key = None

    # the base part of the url for this resource
    base_path = ''

    # The service this belongs to. e.g. 'identity'
    # (unused, is a session/auth_plugin attribute for determining URL)
    service = None

    # limit the abilities of a subclass. You should set these to true if your
    # resource supports that function.
    allow_create = False
    allow_retrieve = False
    allow_update = False
    allow_delete = False
    allow_list = False

    def __init__(self, attrs=None, loaded=False):
        if attrs is None:
            attrs = {}

        self._id = attrs.pop('id', None)
        self._attrs = attrs
        self._dirty = set() if loaded else set(attrs.keys())
        self._loaded = loaded

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
        """Create a new object representation of an existing resource.

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
        # id is read only
        return self._id

    @id.deleter
    def id_del(self):
        self._id = None

    @property
    def is_dirty(self):
        return len(self._dirty) > 0

    def _reset_dirty(self):
        self._dirty = set()

    ##
    # CRUD OPERATIONS
    ##

    @classmethod
    def create_by_id(cls, session, attrs, r_id=None):
        if not cls.allow_create:
            raise MethodNotSupported('create')

        if cls.resource_key:
            body = {cls.resource_key: attrs}
        else:
            body = attrs

        if r_id:
            url = utils.urljoin(cls.base_path, r_id)
            resp = cls._http_put(session, url, json=body)
        else:
            resp = cls._http_post(session, cls.base_path, json=body)

        resp_body = resp.json()

        if cls.resource_key:
            resp_body = resp_body[cls.resource_key]

        return resp_body

    def create(self, session):
        resp_body = self.create_by_id(session, self._attrs, self.id)
        self._id = resp_body.pop('id')
        self._reset_dirty()

    @classmethod
    def get_data_by_id(cls, session, r_id):
        if not cls.allow_retrieve:
            raise MethodNotSupported('retrieve')

        url = utils.urljoin(cls.base_path, r_id)
        body = cls._http_get(session, url).json()

        if cls.resource_key:
            body = body[cls.resource_key]

        return body

    @classmethod
    def get_by_id(cls, session, r_id):
        body = cls.get_data_by_id(session, r_id)
        return cls.existing(**body)

    def get(self, session):
        body = self.get_data_by_id(session, self.id)
        self._attrs.update(body)
        self._loaded = True

    @classmethod
    def update_by_id(cls, session, r_id, attrs):
        if not cls.allow_update:
            raise MethodNotSupported('update')

        if cls.resource_key:
            body = {cls.resource_key: attrs}
        else:
            body = attrs

        url = utils.urljoin(cls.base_path, r_id)
        resp_body = cls._http_patch(session, url, json=body).json()

        if cls.resource_key:
            resp_body = resp_body[cls.resource_key]

        return resp_body

    def update(self, session):
        if not self.is_dirty:
            return

        dirty_attrs = dict((k, self._attrs[k]) for k in self._dirty)
        resp_json = self.update_by_id(session, self.id, dirty_attrs)

        try:
            resp_id = resp_json.pop('id')
        except KeyError:
            pass
        else:
            assert resp_id == self.id

        self._reset_dirty()

    @classmethod
    def delete_by_id(cls, session, r_id):
        if not cls.allow_delete:
            raise MethodNotSupported('delete')

        cls._http_delete(session, utils.urljoin(cls.base_path, r_id))

    def delete(self, session):
        self.delete_by_id(session, self.id)

    @classmethod
    def list(cls, session, limit=None, marker=None):
        # NOTE(jamielennox): Is it possible we can return a generator from here
        # and allow us to keep paging rather than limit and marker?
        if not cls.allow_list:
            raise MethodNotSupported('retrieve')

        filters = {}

        if limit:
            filters['limit'] = limit
        if marker:
            filters['marker'] = marker

        url = cls.base_path
        if filters:
            url = '%s?%s' % (url, url_parse.urlencode(filters))

        resp_body = cls._http_get(session, url).json()

        if cls.resources_key:
            resp_body = resp_body[cls.resources_key]

        return [cls.existing(**data) for data in resp_body]

    ###
    # HTTP Operations
    ###
    # these shouldn't live here long term

    @classmethod
    def _http_request(cls, session, method, path, **kwargs):
        headers = kwargs.setdefault('headers', {})
        headers['Accept'] = 'application/json'

        return session._request(cls.service, path, method, **kwargs)

    @classmethod
    def _http_get(cls, session, url, **kwargs):
        return cls._http_request(session, 'GET', url, **kwargs)

    @classmethod
    def _http_post(cls, session, url, **kwargs):
        return cls._http_request(session, 'POST', url, **kwargs)

    @classmethod
    def _http_put(cls, session, url, **kwargs):
        return cls._http_request(session, 'PUT', url, **kwargs)

    @classmethod
    def _http_patch(cls, session, url, **kwargs):
        return cls._http_request(session, 'PATCH', url, **kwargs)

    @classmethod
    def _http_delete(cls, session, url, **kwargs):
        return cls._http_request(session, 'DELETE', url, **kwargs)

    @classmethod
    def _http_head(cls, session, url, **kwargs):
        return cls._http_request(session, 'HEAD', url, **kwargs)
