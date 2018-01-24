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

from openstack.block_storage import block_storage_service
from openstack import resource


class Pools(resource.Resource):
    resource_key = "pool"
    resources_key = "pools"
    base_path = "/scheduler-stats/get_pools?detail=True"
    service = block_storage_service.BlockStorageService()

    # capabilities
    allow_get = False
    allow_create = False
    allow_delete = False
    allow_list = True

    # Properties
    #: The Cinder name for the pool
    name = resource.Body("name")
    #: returns a dict with information about the pool
    capabilities = resource.Body("capabilities", type=dict)
