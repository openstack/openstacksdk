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

from collections.abc import Generator
from typing import Any

from openstack import exceptions
from openstack import fields
from openstack import resource


class ResourceProviderAllocation(resource.Resource):
    resource_key = None
    resources_key = None
    base_path = '/resource_providers/%(resource_provider_id)s/allocations'

    _query_mapping = resource.QueryParameters(
        include_pagination_defaults=False
    )

    # Capabilities

    allow_list = True

    # Properties

    #: The UUID of a resource provider.
    resource_provider_id = resource.URI('resource_provider_id')
    #: The UUID of the consumer.
    consumer_id = resource.Body('consumer_id', alternate_id=True)
    #: A consistent view marker that assists with the management of concurrent
    #: resource provider updates.
    resource_provider_generation = resource.Body(
        'resource_provider_generation', type=int
    )
    #: The generation of the consumer. Available from microversion 1.28.
    consumer_generation = resource.Body('consumer_generation', type=int)
    #: A dictionary of resource class names to the amount allocated to this
    #: consumer from this resource provider.
    resources = resource.Body('resources', type=dict)

    # TODO(stephenfin): It would be nicer if we could do this in Resource
    # itself since the logic is also found elsewhere (e.g.
    # openstack.identity.v2.extension.Extension) but that code is a bit of a
    # rat's nest right now and needs a spring clean
    @classmethod
    def list(
        cls,
        session: resource.AdapterT,
        paginated: bool = True,
        base_path: str | None = None,
        allow_unknown_params: bool = False,
        *,
        microversion: str | None = None,
        **params: Any,
    ) -> Generator['ResourceProviderAllocation', None, None]:
        """This method is a generator which yields resource objects.

        A re-implementation of :meth:`~openstack.resource.Resource.list` that
        handles placement's single, unpaginated list implementation.

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
        client_filters: dict[str, Any] = {}
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
        uri_params: dict[str, Any] = {}

        for k, v in params.items():
            # We need to gather URI parts to set them on the resource later
            if hasattr(cls, k) and isinstance(getattr(cls, k), fields.URI):
                uri_params[k] = v

        def _dict_filter(f: dict[str, Any], d: dict[str, Any] | None) -> bool:
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

        for consumer_id, allocation_data in data['allocations'].items():
            resource_allocation = {
                'consumer_id': consumer_id,
                'resource_provider_generation': data[
                    'resource_provider_generation'
                ],
                **allocation_data,
                **uri_params,
            }
            value = cls.existing(
                microversion=microversion,
                connection=session._get_connection(),  # type: ignore[attr-defined]
                **resource_allocation,
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
