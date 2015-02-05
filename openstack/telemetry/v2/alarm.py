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
from openstack import utils


class Alarm(resource.Resource):
    id_attribute = 'alarm_id'
    base_path = '/alarms'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    alarm_actions = resource.prop('alarm_actions')
    alarm_id = resource.prop('alarm_id')
    combination_rule = resource.prop('combination_rule')
    description = resource.prop('description')
    enabled = resource.prop('enabled', type=bool)
    insufficient_data_actions = resource.prop('insufficient_data_actions')
    name = resource.prop('name')
    ok_actions = resource.prop('ok_actions')
    project_id = resource.prop('project_id')
    repeat_actions = resource.prop('repeat_actions', type=bool)
    state = resource.prop('state')
    state_changed_at = resource.prop('state_timestamp')
    threshold_rule = resource.prop('threshold_rule')
    time_constraints = resource.prop('time_constraints')
    type = resource.prop('type')
    updated_at = resource.prop('timestamp')
    user_id = resource.prop('user_id')

    def __repr__(self):
        return "alarm: %s" % self._attrs

    def change_state(self, session, next_state):
        """Set the state of an alarm.

           The next_state may be one of: 'ok' 'insufficient data' 'alarm'
        """
        url = utils.urljoin(self.base_path, self.id, 'state')
        resp = session.put(url, service=self.service, json=next_state).body
        return resp

    def check_state(self, session):
        """Retrieve the current state of an alarm from the service.

           The properties of the alarm are not modified.
        """
        url = utils.urljoin(self.base_path, self.id, 'state')
        resp = session.get(url, service=self.service).body
        current_state = resp.replace('\"', '')
        return current_state
