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


class Service(resource.Resource):
    resources_key = 'mservices'
    base_path = '/mservices'

    # capabilities
    allow_list = True

    #: The name of the binary form of the Magnum service.
    binary = resource.Body('binary')
    #: The date and time when the resource was created.
    created_at = resource.Body('created_at')
    #: The disable reason of the service, null if the service is enabled or
    #: disabled without reason provided.
    disabled_reason = resource.Body('disabled_reason')
    #: The host for the service.
    host = resource.Body('host')
    #: The total number of report.
    report_count = resource.Body('report_count')
    #: The current state of Magnum services.
    state = resource.Body('state')
    #: The date and time when the resource was updated.
    updated_at = resource.Body('updated_at')
