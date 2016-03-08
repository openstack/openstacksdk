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
    """.. caution:: This API is a work in progress and is subject to change."""
    resource_key = 'segment'
    resources_key = 'segments'
    base_path = '/segments'
    service = network_service.NetworkService()

    # capabilities
    allow_create = False
    allow_retrieve = True
    allow_update = False
    allow_delete = False
    allow_list = True

    # TODO(rtheis): Add description and name properties when support
    # is available.

    # Properties
    #: The ID of the network associated with this segment.
    network_id = resource.prop('network_id')
    #: The type of network associated with this segment, such as
    #: ``flat``, ``gre``, ``vlan`` or ``vxlan``.
    network_type = resource.prop('network_type')
    #: The name of the physical network associated with this segment.
    physical_network = resource.prop('physical_network')
    #: The segmentation ID for this segment. The network type
    #: defines the segmentation model, VLAN ID for ``vlan`` network type
    #: and tunnel ID for ``gre`` and ``vxlan`` network types. *Type: int*
    segmentation_id = resource.prop('segmentation_id', type=int)
