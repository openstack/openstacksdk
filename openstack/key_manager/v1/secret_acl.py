# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from openstack import resource


class SecretACL(resource.Resource):
    base_path = '/secrets/%(secret_id)s/acl'

    # capabilities
    allow_create = False
    allow_fetch = True  # GET
    allow_commit = True  # PUT, PATCH
    allow_delete = True  # DELETE
    allow_list = False

    # Properties
    #: The UUID of the parent secret used in the URL.
    secret_id = resource.URI('secret_id')
    #: ACL definition for read operations (dict).
    read = resource.Body('read', type=dict)
    #: Reference URL returned by PUT/PATCH.
    acl_ref = resource.Body('acl_ref')
