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


class ServiceProvider(resource.Resource):
    resource_key = 'service_provider'
    resources_key = 'service_providers'
    base_path = '/OS-FEDERATION/service_providers'

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
    #: The URL to authenticate against.
    auth_url = resource.Body('auth_url')
    #: A description of this service provider.
    description = resource.Body('description')
    #: If the service provider is currently enabled.
    is_enabled = resource.Body('enabled', type=bool)
    #: The identifier of the service provider.
    name = resource.Body('id')
    #: The prefix of the RelayState SAML attribute.
    relay_state_prefix = resource.Body('relay_state_prefix')
    #: The service provider's URL.
    sp_url = resource.Body('sp_url')
