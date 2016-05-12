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

from openstack import format
from openstack.network import network_service
from openstack import resource


class Agent(resource.Resource):
    resource_key = 'agent'
    resources_key = 'agents'
    base_path = '/agents'
    service = network_service.NetworkService()

    # capabilities
    allow_create = False
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The type of network agent.
    agent_type = resource.prop('agent_type')
    #: Availability zone for the network agent.
    availability_zone = resource.prop('availability_zone')
    #: The name of the network agent's application binary.
    binary = resource.prop('binary')
    #: Network agent configuration data specific to the agent_type.
    configuration = resource.prop('configurations')
    #: Timestamp when the network agent was created.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    created_at = resource.prop('created_at', type=format.ISO8601)
    #: The network agent description.
    description = resource.prop('description')
    #: Timestamp when the network agent's heartbeat was last seen.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    last_heartbeat_at = resource.prop('heartbeat_timestamp',
                                      type=format.ISO8601)
    #: The host the agent is running on.
    host = resource.prop('host')
    #: The administrative state of the network agent, which is up
    #: ``True`` or down ``False``. *Type: bool*
    is_admin_state_up = resource.prop('admin_state_up', type=bool)
    #: Whether or not the network agent is alive.
    #: *Type: bool*
    is_alive = resource.prop('alive', type=bool)
    #: Timestamp when the network agent was last started.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    started_at = resource.prop('started_at', type=format.ISO8601)
    #: The messaging queue topic the network agent subscribes to.
    topic = resource.prop('topic')
