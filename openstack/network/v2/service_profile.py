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

from openstack.network import network_service
from openstack import resource2 as resource


class ServiceProfile(resource.Resource):
    resource_key = 'service_profile'
    resources_key = 'service_profiles'
    base_path = '/service_profiles'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description', 'driver',
        is_enabled='enabled',
        project_id='tenant_id'
    )
    # Properties
    #: Description of the service flavor profile.
    description = resource.Body('description')
    #: Provider driver for the service flavor profile
    driver = resource.Body('driver')
    #: Sets enabled flag
    is_enabled = resource.Body('enabled', type=bool)
    #: Metainformation of the service flavor profile
    meta_info = resource.Body('metainfo')
    #: The owner project ID
    project_id = resource.Body('tenant_id')
