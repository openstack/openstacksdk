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

from openstack import format
from openstack.key_manager import key_manager_service
from openstack import resource


class Container(resource.Resource):
    id_attribute = 'container_ref'
    resources_key = 'containers'
    base_path = '/containers'
    service = key_manager_service.KeyManagerService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: A URI for this container
    container_ref = resource.prop('container_ref')
    #: The timestamp when this container was created.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    created_at = resource.prop('created', type=format.ISO8601)
    #: The name of this container
    name = resource.prop('name')
    #: A list of references to secrets in this container
    secret_refs = resource.prop('secret_refs')
    #: The status of this container
    status = resource.prop('status')
    #: The type of this container
    type = resource.prop('type')
    #: The timestamp when this container was updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.prop('updated', type=format.ISO8601)
