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

    def fetch_aggregates(self, session):
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

    def set_aggregates(self, session, aggregates=None):
        """Replaces aggregates on the resource provider

        :param session: The session to use for making this request
        :param list aggregates: List of aggregates
        :return: The resource provider with updated aggregates populated
        """
        url = utils.urljoin(self.base_path, self.id, 'aggregates')
        microversion = self._get_microversion(session)

        body = {
            'aggregates': aggregates or [],
        }
        if utils.supports_microversion(session, '1.19'):
            body['resource_provider_generation'] = self.generation

        response = session.put(url, json=body, microversion=microversion)
        exceptions.raise_from_response(response)
        data = response.json()

        updates = {'aggregates': data['aggregates']}
        if 'resource_provider_generation' in data:
            updates['resource_provider_generation'] = data[
                'resource_provider_generation'
            ]
        self._body.attributes.update(updates)

        return self
