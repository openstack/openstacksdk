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

from openstack.block_store import block_store_service
from openstack import resource2


class Type(resource2.Resource):
    resource_key = "volume_type"
    resources_key = "volume_types"
    base_path = "/types"
    service = block_store_service.BlockStoreService()

    # capabilities
    allow_get = True
    allow_create = True
    allow_delete = True
    allow_list = True

    # Properties
    #: A ID representing this type.
    id = resource2.Body("id")
    #: Name of the type.
    name = resource2.Body("name")
    #: A dict of extra specifications. "capabilities" is a usual key.
    extra_specs = resource2.Body("extra_specs", type=dict)
