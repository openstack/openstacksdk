# Copyright (c) 2018, Intel Corporation.
# All Rights Reserved.
#
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


class NetworkSegmentRange(resource.Resource):
    resource_key = 'network_segment_range'
    resources_key = 'network_segment_ranges'
    base_path = '/network_segment_ranges'

    _allow_unknown_attrs_in_body = True

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'name',
        'default',
        'shared',
        'project_id',
        'network_type',
        'physical_network',
        'minimum',
        'maximum',
        'used',
        'available',
        'sort_key',
        'sort_dir',
    )

    # Properties
    #: The network segment range name.
    name = resource.Body('name')
    #: The network segment range is loaded from the host configuration file.
    #: *Type: bool*
    default = resource.Body('default', type=bool)
    #: The network segment range is shared with other projects.
    #: *Type: bool*
    shared = resource.Body('shared', type=bool)
    #: The ID of the project associated with this network segment range.
    project_id = resource.Body('project_id')
    #: The type of network associated with this network segment range, such as
    #:  ``geneve``, ``gre``, ``vlan`` or ``vxlan``.
    network_type = resource.Body('network_type')
    #: The name of the physical network associated with this network segment
    #: range.
    physical_network = resource.Body('physical_network')
    #: The minimum segmentation ID for this network segment range. The
    #: network type defines the segmentation model, VLAN ID for ``vlan``
    #: network type and tunnel ID for ``geneve``, ``gre`` and ``vxlan``
    #: network types.
    #: *Type: int*
    minimum = resource.Body('minimum', type=int)
    #: The maximum segmentation ID for this network segment range. The
    #: network type defines the segmentation model, VLAN ID for ``vlan``
    #: network type and tunnel ID for ``geneve``, ``gre`` and ``vxlan``
    #: network types.
    #: *Type: int*
    maximum = resource.Body('maximum', type=int)
    #: Mapping of which segmentation ID in the range is used by which tenant.
    #: *Type: dict*
    used = resource.Body('used', type=dict)
    #: List of available segmentation IDs in this network segment range.
    #: *Type: list*
    available = resource.Body('available', type=list)
