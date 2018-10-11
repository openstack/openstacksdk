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


class PortGroup(resource.Resource):

    resources_key = 'portgroups'
    base_path = '/portgroups'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'
    commit_jsonpatch = True

    _query_mapping = resource.QueryParameters(
        'node', 'address', 'fields',
    )

    # The mode and properties field introduced in 1.26.
    _max_microversion = '1.26'

    #: The physical hardware address of the portgroup, typically the hardware
    #: MAC address. Added in API microversion 1.23.
    address = resource.Body('address')
    #: Timestamp at which the portgroup was created.
    created_at = resource.Body('created_at')
    #: A set of one or more arbitrary metadata key and value pairs.
    extra = resource.Body('extra', type=dict)
    #: The name of the portgroup
    name = resource.Body('name')
    #: The UUID for the portgroup
    id = resource.Body('uuid', alternate_id=True)
    #: Internal metadaa set and stored by the portgroup.
    internal_info = resource.Body('internal_info')
    #: Whether ports that are members of this portgroup can be used as
    #: standalone ports. Added in API microversion 1.23.
    is_standalone_ports_supported = resource.Body('standalone_ports_supported',
                                                  type=bool)
    #: A list of relative links, including the self and bookmark links.
    links = resource.Body('links', type=list)
    #: Port bonding mode. Added in API microversion 1.26.
    mode = resource.Body('mode')
    #: UUID of the node this portgroup belongs to.
    node_id = resource.Body('node_uuid')
    #: A list of links to the collection of ports belonging to this portgroup.
    #: Added in API microversion 1.24.
    ports = resource.Body('ports')
    #: Port group properties. Added in API microversion 1.26.
    properties = resource.Body('properties', type=dict)
    #: Timestamp at which the portgroup was last updated.
    updated_at = resource.Body('updated_at')


class PortGroupDetail(PortGroup):

    base_path = '/portgroups/detail'

    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'node', 'address',
    )

    #: The UUID for the portgroup
    id = resource.Body('uuid', alternate_id=True)
