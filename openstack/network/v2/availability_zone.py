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
from openstack import resource as _resource


class AvailabilityZone(_resource.Resource):
    resource_key = 'availability_zone'
    resources_key = 'availability_zones'
    base_path = '/availability_zones'
    service = network_service.NetworkService()

    # capabilities
    allow_create = False
    allow_get = False
    allow_update = False
    allow_delete = False
    allow_list = True

    # NOTE: We don't support query by state yet because there is a mapping
    #       at neutron side difficult to map.
    _query_mapping = _resource.QueryParameters(
        name='availability_zone', resource='agent_type')

    # Properties
    #: Name of the availability zone.
    name = _resource.Body('name')
    #: Type of resource for the availability zone, such as ``network``.
    resource = _resource.Body('resource')
    #: State of the availability zone, either ``available`` or
    #: ``unavailable``.
    state = _resource.Body('state')
