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

from openstack import resource


class ServerUsage(resource.Resource):
    resource_key = None
    resources_key = None

    # Capabilities
    allow_create = False
    allow_fetch = False
    allow_delete = False
    allow_list = False
    allow_commit = False

    # Properties
    #: The duration that the server exists (in hours).
    hours = resource.Body('hours')
    #: The display name of a flavor.
    flavor = resource.Body('flavor')
    #: The UUID of the server.
    instance_id = resource.Body('instance_id')
    #: The server name.
    name = resource.Body('name')
    #: The UUID of the project in a multi-tenancy cloud.
    project_id = resource.Body('tenant_id')
    #: The memory size of the server (in MiB).
    memory_mb = resource.Body('memory_mb')
    #: The sum of the root disk size of the server and the ephemeral disk size
    #: of it (in GiB).
    local_gb = resource.Body('local_gb')
    #: The number of virtual CPUs that the server uses.
    vcpus = resource.Body('vcpus')
    #: The date and time when the server was launched.
    started_at = resource.Body('started_at')
    #: The date and time when the server was deleted.
    ended_at = resource.Body('ended_at')
    #: The VM state.
    state = resource.Body('state')
    #: The uptime of the server.
    uptime = resource.Body('uptime')


class Usage(resource.Resource):
    resource_key = 'tenant_usage'
    resources_key = 'tenant_usages'
    base_path = '/os-simple-tenant-usage'

    # Capabilities
    allow_create = False
    allow_fetch = True
    allow_delete = False
    allow_list = True
    allow_commit = False

    # TODO(stephenfin): Add 'start', 'end'. These conflict with the body
    # responses though.
    _query_mapping = resource.QueryParameters(
        "detailed",
        "limit",
        "marker",
        "start",
        "end",
    )

    # Properties
    #: The UUID of the project in a multi-tenancy cloud.
    project_id = resource.Body('tenant_id')
    #: A list of the server usage objects.
    server_usages = resource.Body(
        'server_usages',
        type=list,
        list_type=ServerUsage,
    )
    #: Multiplying the server disk size (in GiB) by hours the server exists,
    #: and then adding that all together for each server.
    total_local_gb_usage = resource.Body('total_local_gb_usage')
    #: Multiplying the number of virtual CPUs of the server by hours the server
    #: exists, and then adding that all together for each server.
    total_vcpus_usage = resource.Body('total_vcpus_usage')
    #: Multiplying the server memory size (in MiB) by hours the server exists,
    #: and then adding that all together for each server.
    total_memory_mb_usage = resource.Body('total_memory_mb_usage')
    #: The total duration that servers exist (in hours).
    total_hours = resource.Body('total_hours')
    #: The beginning time to calculate usage statistics on compute and storage
    #: resources.
    start = resource.Body('start')
    #: The ending time to calculate usage statistics on compute and storage
    #: resources.
    stop = resource.Body('stop')

    _max_microversion = '2.75'
