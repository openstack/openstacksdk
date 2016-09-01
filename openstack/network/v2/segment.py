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
from openstack import resource2 as resource


class Segment(resource.Resource):
    resource_key = 'segment'
    resources_key = 'segments'
    base_path = '/segments'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description', 'name', 'network_id', 'network_type',
        'physical_network', 'segmentation_id',
    )

    # Properties
    #: The segment description.
    description = resource.Body('description')
    #: The segment name.
    name = resource.Body('name')
    #: The ID of the network associated with this segment.
    network_id = resource.Body('network_id')
    #: The type of network associated with this segment, such as
    #: ``flat``, ``geneve``, ``gre``, ``local``, ``vlan`` or ``vxlan``.
    network_type = resource.Body('network_type')
    #: The name of the physical network associated with this segment.
    physical_network = resource.Body('physical_network')
    #: The segmentation ID for this segment. The network type
    #: defines the segmentation model, VLAN ID for ``vlan`` network type
    #: and tunnel ID for ``geneve``, ``gre`` and ``vxlan`` network types.
    #: *Type: int*
    segmentation_id = resource.Body('segmentation_id', type=int)
