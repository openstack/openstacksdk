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

from openstack import exceptions
from openstack import resource
from openstack import utils


class ResourceProvider(resource.Resource):
    resource_key = None
    resources_key = 'resource_providers'
    base_path = '/resource_providers'

    # Capabilities

    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    # Filters

    _query_mapping = resource.QueryParameters(
        'name',
        'member_of',
        'resources',
        'in_tree',
        'required',
        id='uuid',
    )

    # The parent_provider_uuid and root_provider_uuid fields were introduced in
    # 1.14
    # The required query parameter was added in 1.18
    # The create operation started returning a body in 1.20
    _max_microversion = '1.20'

    # Properties

    #: Aggregates
    aggregates = resource.Body('aggregates', type=list, list_type=str)
    #: The UUID of a resource provider.
    id = resource.Body('uuid', alternate_id=True)
    #: A consistent view marker that assists with the management of concurrent
    #: resource provider updates.
    generation = resource.Body('generation')
    #: Links pertaining to this flavor. This is a list of dictionaries,
    #: each including keys ``href`` and ``rel``.
    links = resource.Body('links')
    #: The name of this resource provider.
    name = resource.Body('name')
    #: The UUID of the immediate parent of the resource provider.
    parent_provider_id = resource.Body('parent_provider_uuid')
    #: Read-only UUID of the top-most provider in this provider tree.
    root_provider_id = resource.Body('root_provider_uuid')
    #: Resource class usage counts for this resource provider.
    usages = resource.Body('usages', type=dict)

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
        # The uuid alternate_id gets marked dirty when constructed via new(),
        # which happens inside proxy._update. Placement rejects uuid in the PUT
        # body, so strip it before committing.
        self._body._dirty.discard('uuid')
        return super().commit(
            session,
            prepend_key=prepend_key,
            has_body=has_body,
            retry_on_conflict=retry_on_conflict,
            base_path=base_path,
            microversion=microversion,
            **kwargs,
        )

    def set_inventories(
        self,
        session: adapter.Adapter,
        inventories: dict[str, dict[str, object]],
        resource_provider_generation: int,
    ) -> Self:
        """Replace all inventory records for the resource provider.

        :param session: The session to use for making this request.
        :param inventories: A dict mapping resource class names to inventory
            configuration dicts. Pass an empty dict to remove all inventories.
        :param resource_provider_generation: The generation of the resource
            provider; used to detect concurrent updates.
        :return: The resource provider with the updated generation.
        :raises: :class:`~openstack.exceptions.ConflictException` if the
            generation does not match or there are active allocations against
            an inventory being removed.
        """
        url = utils.urljoin(self.base_path, self.id, 'inventories')
        microversion = self._get_microversion(session)
        body = {
            'resource_provider_generation': resource_provider_generation,
            'inventories': inventories,
        }
        response = session.put(url, json=body, microversion=microversion)
        exceptions.raise_from_response(response)
        data = response.json()
        self._body.attributes.update(
            {'generation': data['resource_provider_generation']}
        )
        return self

    def delete_inventories(self, session: adapter.Adapter) -> None:
        """Delete all inventory records for the resource provider.

        :param session: The session to use for making this request.
        :raises: :class:`~openstack.exceptions.ConflictException` if there are
            active allocations against the resource provider.
        """
        url = utils.urljoin(self.base_path, self.id, 'inventories')
        microversion = self._get_microversion(session)
        response = session.delete(url, microversion=microversion)
        exceptions.raise_from_response(response)

    def fetch_usages(self, session: adapter.Adapter) -> Self:
        """Fetch resource usage counts for the resource provider

        :param session: The session to use for making this request
        :return: The resource provider with usages populated
        """
        url = utils.urljoin(self.base_path, self.id, 'usages')
        microversion = self._get_microversion(session)

        response = session.get(url, microversion=microversion)
        exceptions.raise_from_response(response)
        data = response.json()

        self._body.attributes.update({'usages': data['usages']})

        return self

    def fetch_aggregates(self, session: adapter.Adapter) -> Self:
        """List aggregates set on the resource provider

        :param session: The session to use for making this request
        :return: The resource provider with aggregates populated
        """
        url = utils.urljoin(self.base_path, self.id, 'aggregates')
        microversion = self._get_microversion(session)

        response = session.get(url, microversion=microversion)
        exceptions.raise_from_response(response)
        data = response.json()

        updates = {'aggregates': data['aggregates']}
        if utils.supports_microversion(session, '1.19'):
            updates['generation'] = data['resource_provider_generation']
        self._body.attributes.update(updates)

        return self

    def set_aggregates(
        self,
        session: adapter.Adapter,
        aggregates: list[str] | None = None,
    ) -> Self:
        """Replaces aggregates on the resource provider

        :param session: The session to use for making this request
        :param list aggregates: List of aggregates
        :return: The resource provider with updated aggregates populated
        """
        url = utils.urljoin(self.base_path, self.id, 'aggregates')
        microversion = self._get_microversion(session)

        if utils.supports_microversion(session, '1.19'):
            # 1.19+: body is a dict with aggregates and generation
            body: dict[str, Any] | list[Any] = {
                'aggregates': aggregates or [],
                'resource_provider_generation': self.generation,
            }
        else:
            # pre-1.19: body is a plain list of aggregate UUIDs
            body = aggregates or []

        response = session.put(url, json=body, microversion=microversion)
        exceptions.raise_from_response(response)
        data = response.json()

        # pre-1.19: response is a plain list of aggregate UUIDs
        # 1.19+: response is a dict with 'aggregates' and
        # 'resource_provider_generation'
        if isinstance(data, list):
            updates = {'aggregates': data}
        else:
            updates = {'aggregates': data['aggregates']}
            if 'resource_provider_generation' in data:
                updates['resource_provider_generation'] = data[
                    'resource_provider_generation'
                ]
        self._body.attributes.update(updates)

        return self
