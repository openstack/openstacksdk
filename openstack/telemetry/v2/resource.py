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

from openstack import format
from openstack import resource
from openstack.telemetry import telemetry_service


class Resource(resource.Resource):
    """.. caution:: This API is a work in progress and is subject to change."""
    id_attribute = 'resource_id'
    base_path = '/resources'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_retrieve = True
    allow_list = True

    # Properties
    #: UTC date & time not later than the first sample known
    #: for this resource.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    first_sample_at = resource.prop('first_sample_timestamp',
                                    type=format.ISO8601)
    #: UTC date & time not earlier than the last sample known
    #: for this resource.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    last_sample_at = resource.prop('last_sample_timestamp',
                                   type=format.ISO8601)
    #: A list containing a self link and associated meter links
    links = resource.prop('links')
    #: Arbitrary metadata associated with the resource
    metadata = resource.prop('metadata')
    #: The ID of the owning project
    project_id = resource.prop('project_id')
    #: The ID for the resource
    resource_id = resource.prop('resource_id')
    #: The name of the source where the resource comes from
    source = resource.prop('source')
    #: The ID of the user who created the resource or updated it last
    user_id = resource.prop('user_id')
