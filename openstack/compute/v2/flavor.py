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

from openstack.compute import compute_service
from openstack import resource


class Flavor(resource.Resource):
    resource_key = 'flavor'
    resources_key = 'flavors'
    base_path = '/flavors'
    service = compute_service.ComputeService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        "sort_key", "sort_dir",
        min_disk="minDisk",
        min_ram="minRam")

    # Properties
    #: Links pertaining to this flavor. This is a list of dictionaries,
    #: each including keys ``href`` and ``rel``.
    links = resource.Body('links')
    #: The name of this flavor.
    name = resource.Body('name')
    #: Size of the disk this flavor offers. *Type: int*
    disk = resource.Body('disk', type=int)
    #: ``True`` if this is a publicly visible flavor. ``False`` if this is
    #: a private image. *Type: bool*
    is_public = resource.Body('os-flavor-access:is_public', type=bool)
    #: The amount of RAM (in MB) this flavor offers. *Type: int*
    ram = resource.Body('ram', type=int)
    #: The number of virtual CPUs this flavor offers. *Type: int*
    vcpus = resource.Body('vcpus', type=int)
    #: Size of the swap partitions.
    swap = resource.Body('swap')
    #: Size of the ephemeral data disk attached to this server. *Type: int*
    ephemeral = resource.Body('OS-FLV-EXT-DATA:ephemeral', type=int)
    #: ``True`` if this flavor is disabled, ``False`` if not. *Type: bool*
    is_disabled = resource.Body('OS-FLV-DISABLED:disabled', type=bool)
    #: The bandwidth scaling factor this flavor receives on the network.
    rxtx_factor = resource.Body('rxtx_factor', type=float)


class FlavorDetail(Flavor):
    base_path = '/flavors/detail'

    allow_create = False
    allow_get = False
    allow_update = False
    allow_delete = False
    allow_list = True

    detail_for = Flavor
