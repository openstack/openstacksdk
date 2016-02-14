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


class Meter(resource.Resource):
    """.. caution:: This API is a work in progress and is subject to change."""
    id_attribute = 'meter_id'
    resource_key = 'meter'
    base_path = '/meters'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_list = True

    # Properties
    #: The ID of the meter
    meter_id = resource.prop('meter_id')
    #: The unique name for the meter
    name = resource.prop('name')
    #: The ID of the project that owns the resource
    project_id = resource.prop('project_id')
    #: The ID of the resource for which the measurements are taken
    resource_id = resource.prop('resource_id')
    #: The name of the source where the meter comes from
    source = resource.prop('source')
    #: The meter type
    type = resource.prop('type')
    #: The unit of measure
    unit = resource.prop('unit')
    #: The ID of the user who last triggered an update to the resource
    user_id = resource.prop('user_id')
