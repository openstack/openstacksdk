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


class HealthMonitor(resource.Resource, resource.TagMixin):
    resource_key = 'healthmonitor'
    resources_key = 'healthmonitors'
    base_path = '/lbaas/healthmonitors'

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True
    allow_commit = True

    _query_mapping = resource.QueryParameters(
        'name', 'created_at', 'updated_at', 'delay', 'expected_codes',
        'http_method', 'max_retries', 'max_retries_down', 'pool_id',
        'provisioning_status', 'operating_status', 'timeout',
        'project_id', 'type', 'url_path', is_admin_state_up='admin_state_up',
        **resource.TagMixin._tag_query_parameters
    )

    #: Properties
    #: Timestamp when the health monitor was created.
    created_at = resource.Body('created_at')
    #: The time, in seconds, between sending probes to members.
    delay = resource.Body('delay', type=int)
    #: The expected http status codes to get from a successful health check
    expected_codes = resource.Body('expected_codes')
    #: The HTTP method that the monitor uses for requests
    http_method = resource.Body('http_method')
    #: The administrative state of the health monitor *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: The number of successful checks before changing the operating status
    #: of the member to ONLINE.
    max_retries = resource.Body('max_retries', type=int)
    #: The number of allowed check failures before changing the operating
    #: status of the member to ERROR.
    max_retries_down = resource.Body('max_retries_down', type=int)
    #: The health monitor name
    name = resource.Body('name')
    #: Operating status of the member.
    operating_status = resource.Body('operating_status')
    #: List of associated pools.
    #: *Type: list of dicts which contain the pool IDs*
    pools = resource.Body('pools', type=list)
    #: The ID of the associated Pool
    pool_id = resource.Body('pool_id')
    #: The ID of the project
    project_id = resource.Body('project_id')
    #: The provisioning status of this member.
    provisioning_status = resource.Body('provisioning_status')
    #: The time, in seconds, after which a health check times out
    timeout = resource.Body('timeout', type=int)
    #: The type of health monitor
    type = resource.Body('type')
    #: Timestamp when the member was last updated.
    updated_at = resource.Body('updated_at')
    #: The HTTP path of the request to test the health of a member
    url_path = resource.Body('url_path')
