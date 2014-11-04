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

from openstack.keystore import keystore_service
from openstack import resource


class Secret(resource.Resource):
    id_attribute = 'secret_ref'
    resource_key = 'secret'
    resources_key = 'secrets'
    base_path = '/secrets'
    service = keystore_service.KeystoreService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    algorithm = resource.prop('algorithm')
    bit_length = resource.prop('bit_length')
    content_types = resource.prop('content_types')
    expiration = resource.prop('expiration')
    mode = resource.prop('mode')
    name = resource.prop('name')
    secret_ref = resource.prop('secret_ref')
    status = resource.prop('status')
    updated = resource.prop('updated')
