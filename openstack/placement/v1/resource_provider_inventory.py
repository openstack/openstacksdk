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


class ResourceProviderInventory(resource.Resource):
    resource_key = None
    resources_key = None
    base_path = '/resource_providers/%(resource_provider_id)s/inventories'

    _query_mapping = resource.QueryParameters(
        include_pagination_defaults=False
    )

    # Capabilities

    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Properties

    #: The UUID of a resource provider.
    resource_provider_id = resource.URI('resource_provider_id')
    #: The name of the resource class.
    resource_class = resource.Body('resource_class', alternate_id=True)
    #: A consistent view marker that assists with the management of concurrent
    #: resource provider updates.
    resource_provider_generation = resource.Body(
        'resource_provider_generation',
        type=int,
    )

    #: It is used in determining whether consumption of the resource of the
    #: provider can exceed physical constraints.
    allocation_ratio = resource.Body('allocation_ratio', type=float)
    #: A maximum amount any single allocation against an inventory can have.
    max_unit = resource.Body('max_unit', type=int)
    #: A minimum amount any single allocation against an inventory can have.
    min_unit = resource.Body('min_unit', type=int)
    #: The amount of the resource a provider has reserved for its own use.
    reserved = resource.Body('reserved', type=int)
    #: A representation of the divisible amount of the resource that may be
    #: requested. For example, step_size = 5 means that only values divisible
    #: by 5 (5, 10, 15, etc.) can be requested.
    step_size = resource.Body('step_size', type=int)
    #: The actual amount of the resource that the provider can accommodate.
    total = resource.Body('total', type=int)

    def commit(
        self,
        session,
        prepend_key=True,
        has_body=True,
        retry_on_conflict=None,
        base_path=None,
        *,
        microversion=None,
        **kwargs,
    ):
        # resource_provider_generation must always be provided on update, but
        # it will appear to be identical (by design) so we strip it. Prevent
        # tihs happening.
        self._body._dirty.add('resource_provider_generation')
        return super().commit(
            session,
            prepend_key=prepend_key,
            has_body=has_body,
            retry_on_conflict=retry_on_conflict,
            base_path=base_path,
            microversion=microversion,
            **kwargs,
        )

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

        for resource_class, resource_data in data['inventories'].items():
            resource_inventory = {
                'resource_class': resource_class,
                'resource_provider_generation': data[
                    'resource_provider_generation'
                ],  # noqa: E501
                **resource_data,
                **uri_params,
            }
            value = cls.existing(
                microversion=microversion,
                connection=session._get_connection(),
                **resource_inventory,
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
