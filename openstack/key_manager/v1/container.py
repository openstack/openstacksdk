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

from openstack.key_manager import key_manager_service
from openstack.key_manager.v1 import _format
from openstack import resource2


class Container(resource2.Resource):
    resources_key = 'containers'
    base_path = '/containers'
    service = key_manager_service.KeyManagerService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: A URI for this container
    container_ref = resource2.Body('container_ref')
    #: The ID for this container
    container_id = resource2.Body('container_ref', alternate_id=True,
                                  type=_format.HREFToUUID)
    #: The timestamp when this container was created.
    created_at = resource2.Body('created')
    #: The name of this container
    name = resource2.Body('name')
    #: A list of references to secrets in this container
    secret_refs = resource2.Body('secret_refs', type=list)
    #: The status of this container
    status = resource2.Body('status')
    #: The type of this container
    type = resource2.Body('type')
    #: The timestamp when this container was updated.
    updated_at = resource2.Body('updated')
    #: A party interested in this container.
    consumers = resource2.Body('consumers', type=list)
