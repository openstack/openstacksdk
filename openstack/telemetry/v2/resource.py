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


class Resource(resource.Resource):
    """.. caution:: This API is a work in progress and is subject to change."""
    base_path = '/resources'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_get = True
    allow_list = True

    # Properties
    #: UTC date & time not later than the first sample known
    #: for this resource.
    first_sample_at = resource.Body('first_sample_timestamp')
    #: UTC date & time not earlier than the last sample known
    #: for this resource.
    last_sample_at = resource.Body('last_sample_timestamp')
    #: A list containing a self link and associated meter links
    links = resource.Body('links')
    #: Arbitrary metadata associated with the resource
    metadata = resource.Body('metadata')
    #: The ID of the owning project
    project_id = resource.Body('project_id')
    #: The ID for the resource
    resource_id = resource.Body('resource_id', alternate_id=True)
    #: The name of the source where the resource comes from
    source = resource.Body('source')
    #: The ID of the user who created the resource or updated it last
    user_id = resource.Body('user_id')
