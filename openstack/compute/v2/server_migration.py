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


class ServerMigration(resource.Resource):
    resource_key = 'migration'
    resources_key = 'migrations'
    base_path = '/servers/%(server_id)s/migrations'

    # capabilities
    allow_fetch = True
    allow_list = True
    allow_delete = True

    #: The ID for the server from the URI of the resource
    server_id = resource.URI('server_id')

    #: The date and time when the resource was created.
    created_at = resource.Body('created_at')
    #: The target host of the migration.
    dest_host = resource.Body('dest_host')
    #: The target compute of the migration.
    dest_compute = resource.Body('dest_compute')
    #: The target node of the migration.
    dest_node = resource.Body('dest_node')
    #: The amount of disk, in bytes, that has been processed during the
    #: migration.
    disk_processed_bytes = resource.Body('disk_processed_bytes')
    #: The amount of disk, in bytes, that still needs to be migrated.
    disk_remaining_bytes = resource.Body('disk_remaining_bytes')
    #: The total amount of disk, in bytes, that needs to be migrated.
    disk_total_bytes = resource.Body('disk_total_bytes')
    #: The amount of memory, in bytes, that has been processed during the
    #: migration.
    memory_processed_bytes = resource.Body('memory_processed_bytes')
    #: The amount of memory, in bytes, that still needs to be migrated.
    memory_remaining_bytes = resource.Body('memory_remaining_bytes')
    #: The total amount of memory, in bytes, that needs to be migrated.
    memory_total_bytes = resource.Body('memory_total_bytes')
    #: The ID of the project that initiated the server migration (since
    #: microversion 2.80)
    project_id = resource.Body('project_id')
    #: The UUID of the server from the response body
    server_uuid = resource.Body('server_uuid')
    #: The source compute of the migration.
    source_compute = resource.Body('source_compute')
    #: The source node of the migration.
    source_node = resource.Body('source_node')
    #: The current status of the migration.
    status = resource.Body('status')
    #: The date and time when the resource was last updated.
    updated_at = resource.Body('updated_at')
    #: The ID of the user that initiated the server migration (since
    #: microversion 2.80)
    user_id = resource.Body('user_id')
    #: The UUID of the migration (since microversion 2.59)
    uuid = resource.Body('uuid', alternate_id=True)

    _max_microversion = '2.80'

    def _action(self, session, body):
        """Preform server migration actions given the message body."""
        session = self._get_session(session)
        microversion = self._get_microversion(session)

        url = utils.urljoin(
            self.base_path % {'server_id': self.server_id},
            self.id,
            'action',
        )
        response = session.post(url, microversion=microversion, json=body)
        exceptions.raise_from_response(response)
        return response

    def force_complete(self, session):
        """Force on-going live migration to complete."""
        body = {'force_complete': None}
        self._action(session, body)
