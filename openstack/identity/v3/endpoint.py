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


class Endpoint(resource.Resource):
    resource_key = 'endpoint'
    resources_key = 'endpoints'
    base_path = '/endpoints'
    service = identity_service.IdentityService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    patch_update = True

    # Properties
    #: Describes the interface of the endpoint according to one of the
    #: following values:
    #:
    #: - `public`: intended for consumption by end users, generally on a
    #:     publicly available network interface
    #: - `internal`: not intended for consumption by end users, generally on an
    #:     unmetered internal network interface
    #: - `admin`: intended only for consumption by those needing administrative
    #:     access to the service, generally on a secure network interface
    #:
    #: *Type: string*
    interface = resource.prop('interface')
    #: Setting this value to ``False`` prevents the endpoint from appearing
    #: in the service catalog. *Type: bool*
    is_enabled = resource.prop('enabled', type=bool)
    #: Represents the containing region ID of the service endpoint.
    #: *New in v3.2* *Type: string*
    region_id = resource.prop('region_id')
    #: References the service ID to which the endpoint belongs. *Type: string*
    service_id = resource.prop('service_id')
    #: Fully qualified URL of the service endpoint. *Type: string*
    url = resource.prop('url')
