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
from openstack import resource2 as resource


class Credential(resource.Resource):
    resource_key = 'credential'
    resources_key = 'credentials'
    base_path = '/credentials'
    service = identity_service.IdentityService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True
    patch_update = True

    # Properties
    #: Arbitrary blob of the credential data, to be parsed according to the
    #: ``type``. *Type: string*
    blob = resource.Body('blob')
    #: References a project ID which limits the scope the credential applies
    #: to. This attribute is **mandatory** if the credential type is ``ec2``.
    #: *Type: string*
    project_id = resource.Body('project_id')
    #: Representing the credential type, such as ``ec2`` or ``cert``.
    #: A specific implementation may determine the list of supported types.
    #: *Type: string*
    type = resource.Body('type')
    #: References the user ID which owns the credential. *Type: string*
    user_id = resource.Body('user_id')
