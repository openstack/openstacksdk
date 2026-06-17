# Copyright 2026 SoftBank corp.
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

from typing import Any, Self

from keystoneauth1 import adapter

from openstack import resource


class ResourceProviderTrait(resource.Resource):
    resource_key = None
    resources_key = None
    base_path = '/resource_providers/%(resource_provider_id)s/traits'

    _query_mapping = resource.QueryParameters(
        include_pagination_defaults=False
    )

    requires_id = False
    commit_method = 'PUT'

    # Capabilities

    allow_fetch = True
    allow_commit = True
    allow_delete = True

    # Properties
    #: The UUID of a resource provider.
    resource_provider_id = resource.URI('resource_provider_id')

    #: A consistent view marker that assists with the management of concurrent
    #: resource provider updates.
    resource_provider_generation = resource.Body(
        'resource_provider_generation',
        type=int,
    )

    #: Traits
    traits = resource.Body('traits', type=list, list_type=str)

    # Added in 1.6
    _max_microversion = '1.6'

    def commit(
        self,
        session: adapter.Adapter,
        prepend_key: bool = True,
        has_body: bool = True,
        retry_on_conflict: bool | None = None,
        base_path: str | None = None,
        *,
        microversion: str | None = None,
        **kwargs: Any,
    ) -> Self:
        # resource_provider_generation must always be provided on update, but
        # it will appear to be identical (by design) so we strip it. Prevent
        # this happening.
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

    def fetch(
        self,
        session: adapter.Adapter,
        requires_id: bool = False,
        base_path: str | None = None,
        error_message: str | None = None,
        skip_cache: bool = False,
        *,
        resource_response_key: str | None = None,
        microversion: str | None = None,
        **params: Any,
    ) -> Self:
        # The resource provider trait API doesn't require trait id information.
        return super().fetch(
            session,
            requires_id=False,
            base_path=base_path,
            error_message=error_message,
            skip_cache=skip_cache,
            resource_response_key=resource_response_key,
            microversion=microversion,
            **params,
        )
