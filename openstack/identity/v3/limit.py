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


class Limit(resource.Resource):
    resource_key = 'limit'
    resources_key = 'limits'
    base_path = '/limits'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'
    commit_jsonpatch = True

    _query_mapping = resource.QueryParameters(
        'service_id', 'region_id', 'resource_name', 'project_id'
    )

    # Properties
    #: User-facing description of the registered_limit. *Type: string*
    description = resource.Body('description')
    #: The links for the registered_limit resource.
    links = resource.Body('links')
    #: ID of service. *Type: string*
    service_id = resource.Body('service_id')
    #: ID of region, if any. *Type: string*
    region_id = resource.Body('region_id')
    #: The resource name. *Type: string*
    resource_name = resource.Body('resource_name')
    #: The resource limit value. *Type: int*
    resource_limit = resource.Body('resource_limit')
    #: ID of project. *Type: string*
    project_id = resource.Body('project_id')

    def _prepare_request_body(
        self,
        patch,
        prepend_key,
        *,
        resource_request_key=None,
    ):
        body = self._body.dirty
        if prepend_key and self.resource_key is not None:
            if patch:
                body = {self.resource_key: body}
            else:
                # Keystone support bunch create for unified limit. So the
                # request body for creating limit is a list instead of dict.
                body = {self.resources_key: [body]}
        return body
