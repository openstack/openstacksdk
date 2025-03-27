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
from openstack import fields
from openstack import resource


class MetadefProperty(resource.Resource):
    base_path = '/metadefs/namespaces/%(namespace_name)s/properties'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    #: An identifier (a name) for the namespace.
    namespace_name = resource.URI('namespace_name')
    #: The name of the property
    name = resource.Body('name', alternate_id=True)
    #: The property type.
    type = resource.Body('type')
    #: The title of the property.
    title = resource.Body('title')
    #: Detailed description of the property.
    description = resource.Body('description')
    #: A list of operator
    operators = resource.Body('operators', type=list)
    #: Default property description.
    default = resource.Body('default')
    #: Indicates whether this is a read-only property.
    is_readonly = resource.Body('readonly', type=bool)
    #: Minimum allowed numerical value.
    minimum = resource.Body('minimum', type=int)
    #: Maximum allowed numerical value.
    maximum = resource.Body('maximum', type=int)
    #: Enumerated list of property values.
    enum = resource.Body('enum', type=list)
    #: A regular expression
    #: (`ECMA 262 <http://www.ecma-international.org/publications/standards/Ecma-262.htm>`_)
    #: that a string value must match.
    pattern = resource.Body('pattern')
    #: Minimum allowed string length.
    min_length = resource.Body('minLength', type=int, default=0)
    #: Maximum allowed string length.
    max_length = resource.Body('maxLength', type=int)
    # FIXME(stephenfin): This is causing conflicts due to the 'dict.items'
    # method. Perhaps we need to rename it?
    #: Schema for the items in an array.
    items = resource.Body('items', type=dict)
    #: Indicates whether all values in the array must be distinct.
    require_unique_items = resource.Body(
        'uniqueItems', type=bool, default=False
    )
    #: Minimum length of an array.
    min_items = resource.Body('minItems', type=int, default=0)
    #: Maximum length of an array.
    max_items = resource.Body('maxItems', type=int)
    #: Describes extra items, if you use tuple typing.  If the value of
    #: ``items`` is an array (tuple typing) and the instance is longer than
    #: the list of schemas in ``items``, the additional items are described by
    #: the schema in this property.  If this value is ``false``, the instance
    #: cannot be longer than the list of schemas in ``items``.  If this value
    #: is ``true``, that is equivalent to the empty schema (anything goes).
    allow_additional_items = resource.Body('additionalItems', type=bool)

    # TODO(stephenfin): It would be nicer if we could do this in Resource
    # itself since the logic is also found elsewhere (e.g.
    # openstack.identity.v2.extension.Extension) but that code is a bit of a
    # rat's nest right now and needs a spring clean
    @classmethod
    def list(
        cls,
        session,
        paginated=True,
        base_path=None,
        allow_unknown_params=False,
        *,
        microversion=None,
        **params,
    ):
        """This method is a generator which yields resource objects.

        A re-implementation of :meth:`~openstack.resource.Resource.list` that
        handles glance's single, unpaginated list implementation.

        Refer to :meth:`~openstack.resource.Resource.list` for full
        documentation including parameter, exception and return type
        documentation.
        """
        session = cls._get_session(session)

        if microversion is None:
            microversion = cls._get_microversion(session)

        if base_path is None:
            base_path = cls.base_path

        # There is no server-side filtering, only client-side
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

        uri = base_path % params
        uri_params = {}

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

        response = session.get(
            uri,
            headers={"Accept": "application/json"},
            params={},
            microversion=microversion,
        )
        exceptions.raise_from_response(response)
        data = response.json()

        for name, property_data in data['properties'].items():
            property = {
                'name': name,
                **property_data,
                **uri_params,
            }
            value = cls.existing(
                microversion=microversion,
                connection=session._get_connection(),
                **property,
            )

            filters_matched = True
            # Iterate over client filters and return only if matching
            for key in client_filters.keys():
                if isinstance(client_filters[key], dict):
                    if not _dict_filter(
                        client_filters[key],
                        value.get(key, None),
                    ):
                        filters_matched = False
                        break
                elif value.get(key, None) != client_filters[key]:
                    filters_matched = False
                    break

            if filters_matched:
                yield value

        return None
