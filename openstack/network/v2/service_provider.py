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
    resources_key = 'service_providers'
    base_path = '/service-providers'

    _allow_unknown_attrs_in_body = True

    # Capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'service_type',
        'name',
        is_default='default',
    )

    # Properties
    #: Service type (FIREWALL, FLAVORS, METERING, QOS, etc..)
    service_type = resource.Body('service_type')
    #: Name of the service type
    name = resource.Body('name')
    #: The default value of service type
    is_default = resource.Body('default', type=bool)
