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
from openstack.telemetry.alarm import alarm_service
from openstack import utils


class Alarm(resource.Resource):
    """.. caution:: This API is a work in progress and is subject to change."""
    id_attribute = 'alarm_id'
    base_path = '/alarms'
    service = alarm_service.AlarmService()

    # Supported Operations
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    #: The actions to do when alarm state changes to alarm
    alarm_actions = resource.prop('alarm_actions')
    #: The ID of the alarm
    alarm_id = resource.prop('alarm_id')
    # TODO(briancurtin): undocumented
    combination_rule = resource.prop('combination_rule')
    #: The description of the alarm
    description = resource.prop('description')
    #: ``True`` if this alarm is enabled. *Type: bool*
    is_enabled = resource.prop('enabled', type=bool)
    #: The actions to do when alarm state changes to insufficient data
    insufficient_data_actions = resource.prop('insufficient_data_actions')
    #: The actions should be re-triggered on each evaluation cycle.
    #: *Type: bool*
    is_repeat_actions = resource.prop('repeat_actions', type=bool)
    #: The name for the alarm
    name = resource.prop('name')
    #: The actions to do when alarm state change to ok
    ok_actions = resource.prop('ok_actions')
    #: The ID of the project that owns the alarm
    project_id = resource.prop('project_id')
    #: The severity of the alarm
    severity = resource.prop('severity')
    #: The state off the alarm
    state = resource.prop('state')
    #: The timestamp of the last alarm state change.
    #: *Type: ISO 8601 formatted string*
    state_changed_at = resource.prop('state_timestamp')
    # TODO(briancurtin): undocumented
    threshold_rule = resource.prop('threshold_rule', type=dict)
    #: Describe time constraints for the alarm
    time_constraints = resource.prop('time_constraints')
    #: Explicit type specifier to select which rule to follow
    type = resource.prop('type')
    #: The timestamp of the last alarm definition update.
    #: *Type: ISO 8601 formatted string*
    updated_at = resource.prop('timestamp')
    #: The ID of the user who created the alarm
    user_id = resource.prop('user_id')

    def change_state(self, session, next_state):
        """Set the state of an alarm.

        :param next_state: The valid values can be one of: ``ok``, ``alarm``,
                           ``insufficient data``.
        """
        url = utils.urljoin(self.base_path, self.id, 'state')
        resp = session.put(url, endpoint_filter=self.service, json=next_state)
        return resp.json()

    def check_state(self, session):
        """Retrieve the current state of an alarm from the service.

        The properties of the alarm are not modified.
        """
        url = utils.urljoin(self.base_path, self.id, 'state')
        resp = session.get(url, endpoint_filter=self.service)
        resp = resp.json()
        current_state = resp.replace('\"', '')
        return current_state
