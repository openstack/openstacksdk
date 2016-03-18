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


class Statistics(resource.Resource):
    """.. caution:: This API is a work in progress and is subject to change."""
    id_attribute = 'meter_name'
    resource_key = 'statistics'
    base_path = '/meters/%(meter_name)s/statistics'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_list = True

    # Path Parameter
    meter_name = resource.prop('meter_name')

    # Properties
    #: The selectable aggregate value(s)
    aggregate = resource.prop('aggregate')
    #: The average of all of the volume values seen in the data
    avg = resource.prop('avg')
    #: The number of samples seen
    count = resource.prop('count')
    #: The difference, in seconds, between the oldest and newest timestamp
    duration = resource.prop('duration')
    #: UTC date and time of the oldest timestamp, or the query end time.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    duration_end_at = resource.prop('duration_end', type=format.ISO8601)
    #: UTC date and time of the earliest timestamp, or the query start time.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    duration_start_at = resource.prop('duration_start', type=format.ISO8601)
    #: Dictionary of field names for group, if groupby statistics are requested
    group_by = resource.prop('groupby')
    #: The maximum volume seen in the data
    max = resource.prop('max')
    #: The minimum volume seen in the data
    min = resource.prop('min')
    #: The difference, in seconds, between the period start and end
    period = resource.prop('period')
    #: UTC date and time of the period end.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    period_end_at = resource.prop('period_end', type=format.ISO8601)
    #: UTC date and time of the period start.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    period_start_at = resource.prop('period_start', type=format.ISO8601)
    #: The total of all of the volume values seen in the data
    sum = resource.prop('sum')
    #: The unit type of the data set
    unit = resource.prop('unit')

    @classmethod
    def list(cls, session, limit=None, marker=None, path_args=None,
             paginated=False, **params):
        url = cls._get_url(path_args)
        resp = session.get(url, endpoint_filter=cls.service, params=params)
        for stat in resp.json():
            yield cls.existing(**stat)
