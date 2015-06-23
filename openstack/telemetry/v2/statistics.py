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


class Statistics(resource.Resource):
    id_attribute = 'meter_name'
    resource_key = 'statistics'
    base_path = '/meters/%(meter_name)s/statistics'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_list = True

    # Path Parameter
    meter_name = resource.prop('meter_name')

    # Properties
    aggregate = resource.prop('aggregate')
    avg = resource.prop('avg')
    count = resource.prop('count')
    duration = resource.prop('duration')
    duration_end = resource.prop('duration_end')
    duration_start = resource.prop('duration_start')
    group_by = resource.prop('groupby')
    max = resource.prop('max')
    min = resource.prop('min')
    period = resource.prop('period')
    period_end = resource.prop('period_end')
    period_start = resource.prop('period_start')
    sum = resource.prop('sum')
    unit = resource.prop('unit')

    @classmethod
    def list(cls, session, limit=None, marker=None, path_args=None,
             paginated=False, **params):
        url = cls._get_url(path_args)
        for stat in session.get(url, service=cls.service, params=params).body:
            yield cls.existing(**stat)
