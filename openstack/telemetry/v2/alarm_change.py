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


class AlarmChange(resource.Resource):
    id_attribute = 'event_id'
    resource_key = 'alarm_change'
    base_path = '/alarms/%(alarm_id)s/history'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_list = True

    # Properties
    alarm_id = resource.prop('alarm_id')
    detail = resource.prop('detail')
    event_id = resource.prop('event_id')
    on_behalf_of = resource.prop('on_behalf_of')
    project_id = resource.prop('project_id')
    triggered_at = resource.prop('timestamp')
    type = resource.prop('type')
    user_id = resource.prop('user_id')

    @classmethod
    def list(cls, session, path_args=None, **params):
        url = cls.base_path % path_args
        resp = session.get(url, service=cls.service, params=params)

        changes = []
        for item in resp.body:
            changes.append(cls.existing(**item))
        return changes
