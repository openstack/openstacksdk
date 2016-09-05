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


class Statistics(resource.Resource):
    """.. caution:: This API is a work in progress and is subject to change."""
    resource_key = 'statistics'
    base_path = '/meters/%(meter_name)s/statistics'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_list = True

    # Properties
    #: The selectable aggregate value(s)
    aggregate = resource.Body('aggregate')
    #: The average of all of the volume values seen in the data
    avg = resource.Body('avg')
    #: The number of samples seen
    count = resource.Body('count')
    #: The difference, in seconds, between the oldest and newest timestamp
    duration = resource.Body('duration')
    #: UTC date and time of the oldest timestamp, or the query end time.
    duration_end_at = resource.Body('duration_end')
    #: UTC date and time of the earliest timestamp, or the query start time.
    duration_start_at = resource.Body('duration_start')
    #: Dictionary of field names for group, if groupby statistics are requested
    group_by = resource.Body('groupby')
    #: The maximum volume seen in the data
    max = resource.Body('max')
    #: The minimum volume seen in the data
    min = resource.Body('min')
    #: The difference, in seconds, between the period start and end
    period = resource.Body('period')
    #: UTC date and time of the period end.
    period_end_at = resource.Body('period_end')
    #: UTC date and time of the period start.
    period_start_at = resource.Body('period_start')
    #: The total of all of the volume values seen in the data
    sum = resource.Body('sum')
    #: The unit type of the data set
    #: TODO(Qiming): This is still incorrect
    unit = resource.Body('unit', alternate_id=True)

    @classmethod
    def list(cls, session, paginated=False, **params):
        url = cls.base_path % {'meter_name': params.pop('meter_name')}
        resp = session.get(url, endpoint_filter=cls.service, params=params)
        for stat in resp.json():
            yield cls.existing(**stat)
