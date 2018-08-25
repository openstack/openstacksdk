# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack import resource


class Service(resource.Resource):
    resource_key = 'service'
    resources_key = 'services'
    base_path = '/services'

    # Capabilities
    allow_list = True

    # Properties
    #: Status of service
    status = resource.Body('status')
    #: State of service
    state = resource.Body('state')
    #: Name of service
    binary = resource.Body('binary')
    #: Disabled reason of service
    disabled_reason = resource.Body('disabled_reason')
    #: Host where service runs
    host = resource.Body('host')
    #: The timestamp the service was last updated.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    updated_at = resource.Body('updated_at')
