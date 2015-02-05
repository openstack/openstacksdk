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


class SecurityGroupRule(resource.Resource):
    resource_key = 'security_group_rule'
    resources_key = 'security_group_rules'
    base_path = '/security-group-rules'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    put_update = True

    # Properties
    direction = resource.prop('direction')
    ethertype = resource.prop('ethertype')
    port_range_max = resource.prop('port_range_max')
    port_range_min = resource.prop('port_range_min')
    project_id = resource.prop('tenant_id')
    protocol = resource.prop('protocol')
    remote_group_id = resource.prop('remote_group_id')
    remote_ip_prefix = resource.prop('remote_ip_prefix')
    security_group_id = resource.prop('security_group_id')
