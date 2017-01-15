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
from openstack.workflow import workflow_service


class Execution(resource.Resource):
    resource_key = 'execution'
    resources_key = 'executions'
    base_path = '/executions'
    service = workflow_service.WorkflowService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_get = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        'marker', 'limit', 'sort_keys', 'sort_dirs', 'fields', 'params',
        'include_output')

    workflow_name = resource.Body("workflow_name")
    workflow_id = resource.Body("workflow_id")
    description = resource.Body("description")
    task_execution_id = resource.Body("task_execution_id")
    status = resource.Body("state")
    status_info = resource.Body("state_info")
    input = resource.Body("input")
    output = resource.Body("output")
    created_at = resource.Body("created_at")
    updated_at = resource.Body("updated_at")

    def create(self, session, prepend_key=True):
        request = self._prepare_request(requires_id=False,
                                        prepend_key=prepend_key)

        request_body = request.body["execution"]
        response = session.post(request.uri,
                                endpoint_filter=self.service,
                                json=request_body,
                                headers=request.headers)

        self._translate_response(response, has_body=True)
        return self
