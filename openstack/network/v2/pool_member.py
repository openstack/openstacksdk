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


class PoolMember(resource.Resource):
    resource_key = 'member'
    resources_key = 'members'
    base_path = '/lbaas/pools/%(pool_id)s/members'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The IP address of the pool member.
    address = resource.prop('address')
    #: The administrative state of the pool member, which is up ``True`` or
    #: down ``False``. *Type: bool*
    is_admin_state_up = resource.prop('admin_state_up', type=bool)
    #: Name of the pool member.
    name = resource.prop('name')
    #: The ID of the project this pool member is associated with.
    project_id = resource.prop('tenant_id')
    #: The port on which the application is hosted.
    protocol_port = resource.prop('protocol_port', type=int)
    #: Subnet ID in which to access this pool member.
    subnet_id = resource.prop('subnet_id')
    #: A positive integer value that indicates the relative portion of traffic
    #: that this member should receive from the pool. For example, a member
    #: with a weight of 10 receives five times as much traffic as a member
    #: with weight of 2.
    weight = resource.prop('weight', type=int)

    @classmethod
    def _get_create_body(cls, attrs):
        # Exclude pool_id from attrs since it is not expected by LBaaS service
        if 'pool_id' in attrs:
            attrs.pop('pool_id')

        return {cls.resource_key: attrs}
