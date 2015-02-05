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


class Sample(resource.Resource):
    id_attribute = 'sample_id'
    base_path = '/meters/%(meter)s'
    service = telemetry_service.TelemetryService()

    # Supported Operations
    allow_create = True
    allow_list = True

    # Properties
    metadata = resource.prop('metadata', alias='resource_metadata')
    meter = resource.prop('meter', alias='counter_name')
    project_id = resource.prop('project_id')
    recorded_at = resource.prop('recorded_at')
    resource_id = resource.prop('resource_id')
    sample_id = resource.prop('id', alias='message_id')
    source = resource.prop('source')
    generated_at = resource.prop('timestamp')
    type = resource.prop('type', alias='counter_type')
    unit = resource.prop('unit', alias='counter_unit')
    user_id = resource.prop('user_id')
    volume = resource.prop('volume', alias='counter_volume')

    def __repr__(self):
        return "sample: %s" % self._attrs

    @classmethod
    def list(cls, session, path_args=None, **params):
        url = cls.base_path % path_args
        resp = session.get(url, service=cls.service, params=params)

        changes = []
        for item in resp.body:
            changes.append(cls.existing(**item))
        return changes

    def create(self, session):
        url = self.base_path % {'meter': self.meter}
        # telemetry expects a list of samples
        resp = session.post(url, service=self.service, json=[self._attrs])

        sample = self.existing(**resp.body.pop())
        self._attrs['id'] = sample.id
        self._reset_dirty()
