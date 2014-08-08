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
from openstack.telemetry import telemetry_service


class Capabilities(resource.Resource):
    resource_key = 'capabilities'
    resources_key = 'capabilities'
    base_path = '/v2.0/capabilities'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_list = True

    # Properties
    capabilities = resource.prop('api')
