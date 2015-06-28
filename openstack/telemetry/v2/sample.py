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
    #: Arbitrary metadata associated with the sample
    metadata = resource.prop('metadata', alias='resource_metadata')
    #: The meter name this sample is for
    meter = resource.prop('meter', alias='counter_name')
    #: The project this sample was taken for
    project_id = resource.prop('project_id')
    #: When the sample has been recorded
    recorded_at = resource.prop('recorded_at')
    #: The Resource this sample was taken for
    resource_id = resource.prop('resource_id')
    #: The unique identifier for the sample
    sample_id = resource.prop('id', alias='message_id')
    #: The source that identifies where the sample comes from
    source = resource.prop('source')
    #: When the sample has been generated
    generated_at = resource.prop('timestamp')
    #: The meter type
    type = resource.prop('type', alias='counter_type')
    #: The unit of measure
    unit = resource.prop('unit', alias='counter_unit')
    #: The user this sample was taken for
    user_id = resource.prop('user_id')
    #: The metered value
    volume = resource.prop('volume', alias='counter_volume')

    @classmethod
    def list(cls, session, path_args=None, **params):
        url = cls._get_url(path_args)
        resp = session.get(url, service=cls.service, params=params)

        changes = []
        for item in resp.body:
            changes.append(cls.existing(**item))
        return changes

    def create(self, session):
        url = self._get_url(self)
        # telemetry expects a list of samples
        resp = session.post(url, service=self.service, json=[self._attrs])

        sample = self.existing(**resp.body.pop())
        self._attrs['id'] = sample.id
        self._reset_dirty()
