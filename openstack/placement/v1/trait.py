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


class Trait(resource.Resource):
    resource_key = None
    resources_key = None
    base_path = '/traits'

    # Capabilities

    allow_create = True
    allow_fetch = True
    allow_delete = True
    allow_list = True

    create_method = 'PUT'

    # Added in 1.6
    _max_microversion = '1.6'

    _query_mapping = resource.QueryParameters(
        'name',
        'associated',
        include_pagination_defaults=False,
    )

    name = resource.Body('name', alternate_id=True)

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
        handles the list of strings (as opposed to a list of objects) that this
        call returns.

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

        for trait_name in data['traits']:
            trait = {
                'name': trait_name,
                **uri_params,
            }
            value = cls.existing(
                microversion=microversion,
                connection=session._get_connection(),
                **trait,
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
