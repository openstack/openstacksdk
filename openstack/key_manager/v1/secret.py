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


class Secret(resource.Resource):
    id_attribute = 'secret_ref'
    resources_key = 'secrets'
    base_path = '/secrets'
    service = key_manager_service.KeyManagerService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: Metadata provided by a user or system for informational purposes
    algorithm = resource.prop('algorithm')
    #: Metadata provided by a user or system for informational purposes.
    #: Value must be greater than zero.
    bit_length = resource.prop('bit_length')
    #: A list of content types
    content_types = resource.prop('content_types')
    #: Once this timestamp has past, the secret will no longer be available.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    expires_at = resource.prop('expiration', type=format.ISO8601)
    #: The type/mode of the algorithm associated with the secret information.
    mode = resource.prop('mode')
    #: The name of the secret set by the user
    name = resource.prop('name')
    #: A URI to the sercret
    secret_ref = resource.prop('secret_ref')
    #: The status of this secret
    status = resource.prop('status')
    #: A timestamp when this secret was updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.prop('updated', type=format.ISO8601)
