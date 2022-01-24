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

from openstack import resource


class Migration(resource.Resource):
    resources_key = 'migrations'
    base_path = '/os-migrations'

    # capabilities
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'host',
        'status',
        'migration_type',
        'source_compute',
        'user_id',
        'project_id',
        changes_since='changes-since',
        changes_before='changes-before',
        server_id='instance_uuid',
    )

    #: The date and time when the resource was created.
    created_at = resource.Body('created_at')
    #: The target compute of the migration.
    dest_compute = resource.Body('dest_compute')
    #: The target host of the migration.
    dest_host = resource.Body('dest_host')
    #: The target node of the migration.
    dest_node = resource.Body('dest_node')
    #: The type of the migration. One of 'migration', 'resize',
    #: 'live-migration' or 'evacuation'
    migration_type = resource.Body('migration_type')
    #: The ID of the old flavor. This value corresponds to the ID of the flavor
    #: in the database. This will be the same as new_flavor_id except for
    #: resize operations.
    new_flavor_id = resource.Body('new_instance_type_id')
    #: The ID of the old flavor. This value corresponds to the ID of the flavor
    #: in the database.
    old_flavor_id = resource.Body('old_instance_type_id')
    #: The ID of the project that initiated the server migration (since
    #: microversion 2.80)
    project_id = resource.Body('project_id')
    #: The UUID of the server
    server_id = resource.Body('instance_uuid')
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
