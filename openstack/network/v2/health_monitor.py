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

from openstack.network import network_service
from openstack import resource


class HealthMonitor(resource.Resource):
    resource_key = 'healthmonitor'
    resources_key = 'healthmonitors'
    base_path = '/lbaas/healthmonitors'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The time, in seconds, between sending probes to members.
    delay = resource.prop('delay')
    #: Expected HTTP codes for a passing HTTP(S) monitor.
    expected_codes = resource.prop('expected_codes')
    #: The HTTP method that the monitor uses for requests.
    http_method = resource.prop('http_method')
    #: The administrative state of the health monitor, which is up
    #: ``True`` or down ``False``. *Type: bool*
    is_admin_state_up = resource.prop('admin_state_up', type=bool)
    #: Maximum consecutive health probe tries.
    max_retries = resource.prop('max_retries')
    #: Name of the health monitor.
    name = resource.prop('name')
    #: List of pools associated with this health monitor
    #: *Type: list of dicts which contain the pool IDs*
    pool_ids = resource.prop('pools', type=list)
    #: The ID of the project this health monitor is associated with.
    project_id = resource.prop('tenant_id')
    #: The maximum number of seconds for a monitor to wait for a connection
    #: to be established before it times out. This value must be less than
    #: the delay value.
    timeout = resource.prop('timeout')
    #: The type of probe sent by the load balancer to verify the member
    #: state, which is PING, TCP, HTTP, or HTTPS.
    type = resource.prop('type')
    #: Path portion of URI that will be probed if type is HTTP(S).
    url_path = resource.prop('url_path')
