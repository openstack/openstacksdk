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

from openstack.identity import identity_service
from openstack import resource


class Credential(resource.Resource):
    resource_key = 'credential'
    resources_key = 'credentials'
    base_path = '/credentials'
    service = identity_service.IdentityService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    blob = resource.prop('blob')
    project_id = resource.prop('project_id')
    type = resource.prop('type')
    user_id = resource.prop('user_id')
