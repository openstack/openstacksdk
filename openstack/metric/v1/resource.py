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
from openstack.metric import metric_service
from openstack import resource
from openstack import resource_types


class Generic(resource.Resource):
    base_path = '/resource/generic'
    service = metric_service.MetricService()

    # Supported Operations
    allow_create = True
    allow_retrieve = True
    allow_delete = True
    allow_list = True
    allow_update = True

    # Properties
    id = resource.prop('id', alias="resource_id")
    created_by_user_id = resource.prop('created_by_user_id')
    created_by_project_id = resource.prop('created_by_project_id')
    user_id = resource.prop('user_id')
    project_id = resource.prop('project_id')
    started_at = resource.prop('started_at',
                               type=resource_types.ISO8601Datetime)
    ended_at = resource.prop('ended_at',
                             type=resource_types.ISO8601Datetime)
    metrics = resource.prop('metrics', type=dict)

    def create(self, session):
        resp = self.create_by_id(session, self._attrs, None, path_args=self)
        self._attrs[self.id_attribute] = resp[self.id_attribute]
        self._reset_dirty()
        return self
