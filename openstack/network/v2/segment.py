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


class Segment(resource.Resource):
    resource_key = 'segment'
    resources_key = 'segments'
    base_path = '/segments'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The segment description.
    description = resource.prop('description')
    #: The segment name.
    name = resource.prop('name')
    #: The ID of the network associated with this segment.
    network_id = resource.prop('network_id')
    #: The type of network associated with this segment, such as
    #: ``flat``, ``geneve``, ``gre``, ``local``, ``vlan`` or ``vxlan``.
    network_type = resource.prop('network_type')
    #: The name of the physical network associated with this segment.
    physical_network = resource.prop('physical_network')
    #: The segmentation ID for this segment. The network type
    #: defines the segmentation model, VLAN ID for ``vlan`` network type
    #: and tunnel ID for ``geneve``, ``gre`` and ``vxlan`` network types.
    #: *Type: int*
    segmentation_id = resource.prop('segmentation_id', type=int)
