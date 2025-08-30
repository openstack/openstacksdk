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

from openstack.key_manager.v1 import _format
from openstack import resource


class SecretStore(resource.Resource):
    resources_key = 'secret_stores'
    base_path = '/secret-stores'

    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = True

    _query_mapping = resource.QueryParameters(
        "name",
        "status",
        "global_default",
        "crypto_plugin",
        "secret_store_plugin",
        "created",
        "updated",
    )

    # Properties
    #: The name of the secret store
    name = resource.Body('name')
    #: The status of the secret store
    status = resource.Body('status')
    #: Timestamp of when the secret store was created
    created_at = resource.Body('created')
    #: Timestamp of when the secret store was last updated
    updated_at = resource.Body('updated')
    #: A URI to the secret store
    secret_store_ref = resource.Body('secret_store_ref')
    #: The ID of the secret store
    secret_store_id = resource.Body(
        'secret_store_ref', alternate_id=True, type=_format.HREFToUUID
    )
    #: Flag indicating if this secret store is global default
    global_default = resource.Body('global_default', type=bool)
    #: The crypto plugin name
    crypto_plugin = resource.Body('crypto_plugin')
    #: The secret store plugin name
    secret_store_plugin = resource.Body('secret_store_plugin')
