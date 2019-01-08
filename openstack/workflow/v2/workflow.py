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


class Workflow(resource.Resource):
    resource_key = 'workflow'
    resources_key = 'workflows'
    base_path = '/workflows'

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        'marker', 'limit', 'sort_keys', 'sort_dirs', 'fields')

    #: The name of this Workflow
    name = resource.Body("name")
    #: The inputs for this Workflow
    input = resource.Body("input")
    #: A Workflow definition using the Mistral v2 DSL
    definition = resource.Body("definition")
    #: A list of values associated with a workflow that users can use
    #: to group workflows by some criteria
    # TODO(briancurtin): type=list
    tags = resource.Body("tags")
    #: Can be either "private" or "public"
    scope = resource.Body("scope")
    #: The ID of the associated project
    project_id = resource.Body("project_id")
    #: The time at which the workflow was created
    created_at = resource.Body("created_at")
    #: The time at which the workflow was created
    updated_at = resource.Body("updated_at")

    def create(self, session, prepend_key=True, base_path=None):
        request = self._prepare_request(requires_id=False,
                                        prepend_key=prepend_key,
                                        base_path=base_path)

        headers = {
            "Content-Type": 'text/plain'
        }
        kwargs = {
            "data": self.definition,
        }

        scope = "?scope=%s" % self.scope
        uri = request.url + scope

        request.headers.update(headers)
        response = session.post(uri,
                                json=None,
                                headers=request.headers, **kwargs)

        self._translate_response(response, has_body=False)
        return self
