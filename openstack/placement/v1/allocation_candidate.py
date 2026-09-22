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
from openstack import resource


class AllocationCandidate(resource.Resource):
    """A single candidate set of allocations.

    Represents one entry from ``allocation_requests`` in the placement
    allocation candidates response, with the corresponding
    ``provider_summaries`` data filtered to only the resource providers
    referenced by this candidate.

    An ``AllocationCandidate`` contains enough information to issue a
    :meth:`~openstack.placement.v1._proxy.Proxy.update_allocation` call: the
    ``allocations`` dict maps resource provider UUIDs to the resources to
    request from each, while ``provider_summaries`` supplies the capacity and
    trait information for those providers to help choose between candidates.
    """

    resource_key = None
    resources_key = None
    base_path = '/allocation_candidates'

    requires_id = False
    allow_list = True

    # Available from 1.10; 1.34 added mappings inside each allocation request.
    _max_microversion = '1.34'

    # Properties

    #: A dict mapping resource provider UUID to the resources requested from
    #: that provider, e.g. ``{"<rp-uuid>": {"resources": {"VCPU": 1}}}``.
    # type=dict would fail for pre-1.12 list format; accept raw value
    allocations = resource.Body('allocations')
    #: A dict mapping request-group suffixes to the list of resource provider
    #: UUIDs that satisfy that group. Available from microversion 1.34.
    mappings = resource.Body('mappings', type=dict)
    #: A dict keyed by resource provider UUID with capacity and trait
    #: information for each provider referenced in ``allocations``. This is
    #: derived from the top-level ``provider_summaries`` field in the API
    #: response, filtered to only the providers relevant to this candidate.
    provider_summaries = resource.Body('provider_summaries', type=dict)

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
    ) -> Generator['AllocationCandidate', None, None]:
        """This method is a generator which yields resource objects.

        A re-implementation of :meth:`~openstack.resource.Resource.list` that
        handles the allocation candidates response format. The API returns a
        single dict with ``allocation_requests`` (a list) and
        ``provider_summaries`` (a shared dict keyed by resource provider UUID).
        This method yields one :class:`AllocationCandidate` per entry in
        ``allocation_requests``, with ``provider_summaries`` filtered to only
        the resource providers referenced by that candidate.

        Refer to :meth:`~openstack.resource.Resource.list` for full
        documentation including parameter, exception and return type
        documentation.
        """
        session = cls._get_session(session)

        if microversion is None:
            microversion = cls._get_microversion(session)

        if base_path is None:
            base_path = cls.base_path

        response = session.get(
            base_path,
            headers={'Accept': 'application/json'},
            params=params,
            microversion=microversion,
        )
        exceptions.raise_from_response(response)
        data = response.json()

        provider_summaries = data.get('provider_summaries', {})

        for allocation_request in data.get('allocation_requests', []):
            allocations = allocation_request.get('allocations', {})
            # At v1.12+ allocations is a dict keyed by RP UUID.
            # At v1.10-v1.11 it is a list of dicts
            if isinstance(allocations, dict):
                rp_uuids = set(allocations.keys())
            else:
                rp_uuids = {
                    a['resource_provider']['uuid'] for a in allocations
                }
            candidate_summaries = {
                uuid: summary
                for uuid, summary in provider_summaries.items()
                if uuid in rp_uuids
            }

            yield cls.existing(
                microversion=microversion,
                connection=session._get_connection(),  # type: ignore[attr-defined]
                allocations=allocation_request.get('allocations'),
                mappings=allocation_request.get('mappings'),
                provider_summaries=candidate_summaries,
            )

        return None
