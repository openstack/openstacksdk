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


class HealthMonitor(resource.Resource):
    resource_key = 'healthmonitor'
    resources_key = 'healthmonitors'
    base_path = '/lbaas/healthmonitors'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'delay', 'expected_codes', 'http_method', 'max_retries',
        'timeout', 'type', 'url_path',
        is_admin_state_up='adminstate_up',
        project_id='tenant_id',
    )

    # Properties
    #: The time, in seconds, between sending probes to members.
    delay = resource.Body('delay')
    #: Expected HTTP codes for a passing HTTP(S) monitor.
    expected_codes = resource.Body('expected_codes')
    #: The HTTP method that the monitor uses for requests.
    http_method = resource.Body('http_method')
    #: The administrative state of the health monitor, which is up
    #: ``True`` or down ``False``. *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: Maximum consecutive health probe tries.
    max_retries = resource.Body('max_retries')
    #: Name of the health monitor.
    name = resource.Body('name')
    #: List of pools associated with this health monitor
    #: *Type: list of dicts which contain the pool IDs*
    pool_ids = resource.Body('pools', type=list)
    #: The ID of the pool associated with this health monitor
    pool_id = resource.Body('pool_id')
    #: The ID of the project this health monitor is associated with.
    project_id = resource.Body('tenant_id')
    #: The maximum number of seconds for a monitor to wait for a
    #: connection to be established before it times out. This value must
    #: be less than the delay value.
    timeout = resource.Body('timeout')
    #: The type of probe sent by the load balancer to verify the member
    #: state, which is PING, TCP, HTTP, or HTTPS.
    type = resource.Body('type')
    #: Path portion of URI that will be probed if type is HTTP(S).
    url_path = resource.Body('url_path')
