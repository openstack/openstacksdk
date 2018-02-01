# Copyright 2018 Red Hat, Inc.
#
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
"""Doc and Code templates to be used by the Proxy Metaclass.

The doc templates and code templates are stored separately because having
either of them templated is weird in the first place, but having a doc
string inside of a function definition that's inside of a triple-quoted
string is just hard on the eyeballs.
"""

_FIND_TEMPLATE = """Find a single {resource_name}

:param name_or_id: The name or ID of an {resource_name}.
:param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.ResourceNotFound` will be
            raised when the resource does not exist.
            When set to ``True``, None will be returned when
            attempting to find a nonexistent resource.
:returns: One :class:`~{resource_class}` or None
"""

_LIST_TEMPLATE = """Retrieve a generator of all {resource_name}

:param bool details: When ``True``, returns
    :class:`~{detail_class}` objects,
    otherwise :class:`~{resource_class}`.
    *Default: ``True``*
:param kwargs \*\*query: Optional query parameters to be sent to limit
                         the flavors being returned.

:returns: A generator of {resource_name} instances.
:rtype: :class:`~{resource_class}`
"""

_DELETE_TEMPLATE = """Delete a {resource_name}

:param {name}:
    The value can be either the ID of a {name} or a
    :class:`~{resource_class}` instance.
:param bool ignore_missing:
    When set to ``False`` :class:`~openstack.exceptions.ResourceNotFound`
    will be raised when the {name} does not exist.
    When set to ``True``, no exception will be set when
    attempting to delete a nonexistent {name}.

:returns: ``None``
"""

_GET_TEMPLATE = """Get a single {resource_name}

:param {name}:
    The value can be the ID of a {name} or a
    :class:`~{resource_class}` instance.

:returns: One :class:`~{resource_class}`
:raises: :class:`~openstack.exceptions.ResourceNotFound`
         when no resource can be found.
"""

_CREATE_TEMPLATE = """Create a new {resource_name} from attributes

:param dict attrs:
    Keyword arguments which will be used to create a
    :class:`~{resource_class}`.

:returns: The results of {resource_name} creation
:rtype: :class:`~{resource_class}`
"""

_UPDATE_TEMPLATE = """Update a {resource_name}

:param {name}:
    Either the ID of a {resource_name} or a :class:`~{resource_class}`
    instance.
:attrs kwargs:
    The attributes to update on the {resource_name} represented by
    ``{name}``.

:returns: The updated server
:rtype: :class:`~{resource_class}`
"""

_DOC_TEMPLATES = {
    'create': _CREATE_TEMPLATE,
    'delete': _DELETE_TEMPLATE,
    'find': _FIND_TEMPLATE,
    'list': _LIST_TEMPLATE,
    'get': _GET_TEMPLATE,
    'update': _UPDATE_TEMPLATE,
}

_FIND_SOURCE = """
def find(self, name_or_id, ignore_missing=True):
    return self._find(
        self.{resource_name}, name_or_id, ignore_missing=ignore_missing)
"""

_CREATE_SOURCE = """
def create(self, **attrs):
    return self._create(self.{resource_name}, **attrs)
"""

_DELETE_SOURCE = """
def delete(self, {name}, ignore_missing=True):
    self._delete(self.{resource_name}, {name}, ignore_missing=ignore_missing)
"""

_GET_SOURCE = """
def get(self, {name}):
    return self._get(self.{resource_name}, {name})
"""

_LIST_SOURCE = """
def list(self, details=True, **query):
    res_cls = self.{detail_name} if details else self.{resource_name}
    return self._list(res_cls, paginated=True, **query)
"""

_UPDATE_SOURCE = """
def update(self, {name}, **attrs):
    return self._update(self.{resource_name}, {name}, **attrs)
"""

_SOURCE_TEMPLATES = {
    'create': _CREATE_SOURCE,
    'delete': _DELETE_SOURCE,
    'find': _FIND_SOURCE,
    'list': _LIST_SOURCE,
    'get': _GET_SOURCE,
    'update': _UPDATE_SOURCE,
}


def get_source_template(action, **kwargs):
    return _SOURCE_TEMPLATES[action].format(**kwargs)


def get_doc_template(action, **kwargs):
    return _DOC_TEMPLATES[action].format(**kwargs)
