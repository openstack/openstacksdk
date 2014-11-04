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


class Container(resource.Resource):
    id_attribute = 'container_ref'
    resources_key = 'containers'
    base_path = '/containers'
    service = keystore_service.KeystoreService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    container_ref = resource.prop('container_ref')
    created = resource.prop('created')
    name = resource.prop('name')
    secret_refs = resource.prop('secret_refs')
    status = resource.prop('status')
    type = resource.prop('type')
    updated = resource.prop('updated')
