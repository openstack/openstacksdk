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


class AlarmChange(resource.Resource):
    """.. caution:: This API is a work in progress and is subject to change."""
    id_attribute = 'event_id'
    resource_key = 'alarm_change'
    base_path = '/alarms/%(alarm_id)s/history'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_list = True

    # Properties
    #: The ID of the alarm
    alarm_id = resource.prop('alarm_id')
    #: Data describing the change
    detail = resource.prop('detail')
    #: The ID of the change event
    event_id = resource.prop('event_id')
    #: The project ID on behalf of which the change is being made
    on_behalf_of_id = resource.prop('on_behalf_of')
    #: The project ID of the initiating identity
    project_id = resource.prop('project_id')
    #: The time/date of the alarm change.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    triggered_at = resource.prop('timestamp', type=format.ISO8601)
    #: The type of change
    type = resource.prop('type')
    #: The user ID of the initiating identity
    user_id = resource.prop('user_id')

    @classmethod
    def list(cls, session, limit=None, marker=None, path_args=None,
             paginated=False, **params):
        url = cls._get_url(path_args)
        resp = session.get(url, endpoint_filter=cls.service, params=params)
        for item in resp.json():
            yield cls.existing(**item)
