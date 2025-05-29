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

from openstack.baremetal.v1 import _common
from openstack import resource


class Port(_common.Resource):
    resources_key = 'ports'
    base_path = '/ports'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_patch = True
    commit_method = 'PATCH'
    commit_jsonpatch = True

    _query_mapping = resource.QueryParameters(
        'address',
        'node',
        'portgroup',
        'shard',
        fields={'type': _common.fields_type},
        node_id='node_uuid',
    )

    # The physical_network field introduced in 1.34
    # The is_smartnic field added in 1.53
    # Query filter by shard added in 1.82
    # The name field added in 1.88
    # The description field added in 1.97
    _max_microversion = '1.97'

    #: The physical hardware address of the network port, typically the
    #: hardware MAC address.
    address = resource.Body('address')
    #: Timestamp at which the port was created.
    created_at = resource.Body('created_at')
    #: The description for the port
    description = resource.Body('description')
    #: A set of one or more arbitrary metadata key and value pairs.
    extra = resource.Body('extra')
    #: The UUID of the port
    id = resource.Body('uuid', alternate_id=True)
    #: Internal metadata set and stored by the port. This field is read-only.
    #: Added in API microversion 1.18.
    internal_info = resource.Body('internal_info')
    #: Whether PXE is enabled on the port. Added in API microversion 1.19.
    is_pxe_enabled = resource.Body('pxe_enabled', type=bool)
    #: Whether the port is a Smart NIC port. Added in API microversion 1.53.
    is_smartnic = resource.Body('is_smartnic', type=bool)
    #: A list of relative links, including the self and bookmark links.
    links = resource.Body('links', type=list)
    #: The port bindig profile. If specified, must contain ``switch_id`` and
    #: ``port_id`` fields. ``switch_info`` field is an optional string field
    #: to be used to store vendor specific information. Added in API
    #: microversion 1.19.
    local_link_connection = resource.Body('local_link_connection')
    #: The name of the port
    name = resource.Body('name')
    #: The UUID of node this port belongs to
    node_id = resource.Body('node_uuid')
    #: The name of physical network this port is attached to.
    #: Added in API microversion 1.34.
    physical_network = resource.Body('physical_network')
    #: The UUID of PortGroup this port belongs to. Added in API microversion
    #: 1.24.
    port_group_id = resource.Body('portgroup_uuid')
    #: Read-only. The parent port trunk details dictionary, with the trunk ID
    # and the subports information (port ID, segmentation ID and segmentation
    # type).
    trunk_details = resource.Body('trunk_details', type=dict)
    #: Timestamp at which the port was last updated.
    updated_at = resource.Body('updated_at')


PortDetail = Port
