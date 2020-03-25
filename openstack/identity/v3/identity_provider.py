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

from openstack import resource


class IdentityProvider(resource.Resource):
    resource_key = 'identity_provider'
    resources_key = 'identity_providers'
    base_path = '/OS-FEDERATION/identity_providers'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    create_method = 'PUT'
    create_exclude_id_from_body = True
    commit_method = 'PATCH'

    _query_mapping = resource.QueryParameters(
        'id',
        is_enabled='enabled',
    )

    # Properties
    #: The id of a domain associated with this identity provider.
    #  *Type: string*
    domain_id = resource.Body('domain_id')
    #: A description of this identity provider. *Type: string*
    description = resource.Body('description')
    #: If the identity provider is currently enabled. *Type: bool*
    is_enabled = resource.Body('enabled', type=bool)
    #: Remote IDs associated with the identity provider. *Type: list*
    remote_ids = resource.Body('remote_ids', type=list)

    #: The identifier of the identity provider (read only). *Type: string*
    name = resource.Body('id')
