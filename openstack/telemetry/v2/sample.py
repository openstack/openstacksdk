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

from openstack import resource2 as resource
from openstack.telemetry import telemetry_service


class Sample(resource.Resource):
    """.. caution:: This API is a work in progress and is subject to change."""
    base_path = '/meters/%(counter_name)s'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_get = True
    allow_list = True

    # Properties
    #: When the sample has been generated.
    generated_at = resource.Body('timestamp')
    #: The message ID
    message_id = resource.Body('message_id', alternate_id=True)
    #: Arbitrary metadata associated with the sample
    metadata = resource.Body('metadata')
    #: The meter name this sample is for
    counter_name = resource.Body('counter_name')
    #: The meter name this sample is for
    counter_type = resource.Body('counter_type')
    #: The ID of the project this sample was taken for
    project_id = resource.Body('project_id')
    #: When the sample has been recorded.
    recorded_at = resource.Body('recorded_at')
    #: The ID of the resource this sample was taken for
    resource_id = resource.Body('resource_id')
    #: The name of the source that identifies where the sample comes from
    source = resource.Body('source')
    #: The meter type
    type = resource.Body('type')
    #: The unit of measure
    unit = resource.Body('unit')
    #: The ID of the user this sample was taken for
    user_id = resource.Body('user_id')
    #: The metered value
    volume = resource.Body('volume')
