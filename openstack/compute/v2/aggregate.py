# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack import exceptions
from openstack import resource
from openstack import utils


class Aggregate(resource.Resource):
    resource_key = 'aggregate'
    resources_key = 'aggregates'
    base_path = '/os-aggregates'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_delete = True
    allow_list = True
    allow_commit = True

    # Properties
    #: Availability zone of aggregate
    availability_zone = resource.Body('availability_zone')
    #: The date and time when the resource was created.
    created_at = resource.Body('created_at')
    #: The date and time when the resource was deleted.
    deleted_at = resource.Body('deleted_at')
    #: Deleted?
    is_deleted = resource.Body('deleted', type=bool)
    #: Name of aggregate
    name = resource.Body('name')
    #: Hosts
    hosts = resource.Body('hosts', type=list)
    #: Metadata
    metadata = resource.Body('metadata', type=dict)
    #: The date and time when the resource was updated
    updated_at = resource.Body('updated_at')
    #: UUID
    uuid = resource.Body('uuid')
    # Image pre-caching introduced in 2.81
    _max_microversion = '2.81'

    def _action(self, session, body, microversion=None):
        """Preform aggregate actions given the message body."""
        url = utils.urljoin(self.base_path, self.id, 'action')
        response = session.post(
            url, json=body, microversion=microversion)
        exceptions.raise_from_response(response)
        aggregate = Aggregate()
        aggregate._translate_response(response=response)
        return aggregate

    def add_host(self, session, host):
        """Adds a host to an aggregate."""
        body = {'add_host': {'host': host}}
        return self._action(session, body)

    def remove_host(self, session, host):
        """Removes a host from an aggregate."""
        body = {'remove_host': {'host': host}}
        return self._action(session, body)

    def set_metadata(self, session, metadata):
        """Creates or replaces metadata for an aggregate."""
        body = {'set_metadata': {'metadata': metadata}}
        return self._action(session, body)

    def precache_images(self, session, images):
        """Requests image pre-caching"""
        body = {'cache': images}
        url = utils.urljoin(self.base_path, self.id, 'images')
        response = session.post(
            url, json=body, microversion=self._max_microversion)
        exceptions.raise_from_response(response)
        # This API has no result
