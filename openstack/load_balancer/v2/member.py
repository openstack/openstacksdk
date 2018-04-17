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

from openstack.load_balancer import load_balancer_service as lb_service
from openstack import resource


class Member(resource.Resource):
    resource_key = 'member'
    resources_key = 'members'
    base_path = '/v2.0/lbaas/pools/%(pool_id)s/members'
    service = lb_service.LoadBalancerService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'address', 'name', 'protocol_port', 'subnet_id', 'weight',
        'created_at', 'updated_at', 'provisioning_status', 'operating_status',
        'project_id', 'monitor_address', 'monitor_port', 'backup',
        is_admin_state_up='admin_state_up',
    )

    # Properties
    #: The IP address of the member.
    address = resource.Body('address')
    #: Timestamp when the member was created.
    created_at = resource.Body('created_at')
    #: The administrative state of the member, which is up ``True`` or
    #: down ``False``. *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: IP address used to monitor this member
    monitor_address = resource.Body('monitor_address')
    #: Port used to monitor this member
    monitor_port = resource.Body('monitor_port', type=int)
    #: Name of the member.
    name = resource.Body('name')
    #: Operating status of the member.
    operating_status = resource.Body('operating_status')
    #: The ID of the owning pool.
    pool_id = resource.URI('pool_id')
    #: The provisioning status of this member.
    provisioning_status = resource.Body('provisioning_status')
    #: The ID of the project this member is associated with.
    project_id = resource.Body('project_id')
    #: The port on which the application is hosted.
    protocol_port = resource.Body('protocol_port', type=int)
    #: Subnet ID in which to access this member.
    subnet_id = resource.Body('subnet_id')
    #: Timestamp when the member was last updated.
    updated_at = resource.Body('updated_at')
    #: A positive integer value that indicates the relative portion of traffic
    #: that this member should receive from the pool. For example, a member
    #: with a weight of 10 receives five times as much traffic as a member
    #: with weight of 2.
    weight = resource.Body('weight', type=int)
    #: A bool value that indicates whether the member is a backup or not.
    #: Backup members only receive traffic when all non-backup members
    #: are down.
    backup = resource.Body('backup', type=bool)
