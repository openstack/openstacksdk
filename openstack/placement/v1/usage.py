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


class Usage(resource.Resource):
    """Resource usage for one consumer type within a project.

    Represents one entry from the ``usages`` dict returned by
    ``GET /usages``. Each entry is keyed by consumer type (e.g. ``INSTANCE``,
    ``MIGRATION``) and contains:

    - ``consumer_count`` — the number of consumers of that type with active
      allocations in the project.
    - ``resources`` — a dict of resource class name to total amount consumed
      across all consumers of that type.

    Available from placement microversion 1.38. Call
    :meth:`~openstack.placement.v1._proxy.Proxy.usages` to retrieve instances.
    """

    resource_key = None
    resources_key = None
    base_path = '/usages'

    requires_id = False
    allow_list = True

    # Requires microversion 1.38 for the consumer-type-keyed response format.
    _max_microversion = '1.38'

    # Properties

    #: The consumer type string, e.g. ``INSTANCE`` or ``MIGRATION``.
    consumer_type = resource.Body('consumer_type')
    #: The number of consumers of this type with active allocations.
    consumer_count = resource.Body('consumer_count', type=int)
    #: A dict of resource class name to total amount consumed across all
    #: consumers of this type, e.g. ``{"VCPU": 2, "DISK_GB": 5}``.
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
    ) -> Generator['Usage', None, None]:
        """This method is a generator which yields resource objects.

        A re-implementation of :meth:`~openstack.resource.Resource.list` that
        handles the ``GET /usages`` response format. The API returns a single
        ``usages`` dict keyed by consumer type; this method yields one
        :class:`Usage` per entry, with the per-resource-class amounts packed
        into the ``resources`` field.

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
            params={k: v for k, v in params.items() if v is not None},
            microversion=microversion,
        )
        exceptions.raise_from_response(response)
        data = response.json()

        usages_data = data.get('usages', {})
        first_value = next(iter(usages_data.values()), None)
        if isinstance(first_value, dict):
            # v1.38+ format:
            # {consumer_type: {consumer_count: N, RC: count, ...}}
            for consumer_type, usage_data in usages_data.items():
                resources = {}
                consumer_count = None
                for key, value in usage_data.items():
                    if key == 'consumer_count':
                        consumer_count = value
                    else:
                        resources[key] = value

                yield cls.existing(
                    microversion=microversion,
                    connection=session._get_connection(),  # type: ignore[attr-defined]
                    consumer_type=consumer_type,
                    consumer_count=consumer_count,
                    resources=resources,
                )
        else:
            # pre-1.38 format: {resource_class: count}
            yield cls.existing(
                microversion=microversion,
                connection=session._get_connection(),  # type: ignore[attr-defined]
                consumer_type=None,
                consumer_count=None,
                resources=usages_data,
            )

        return None
