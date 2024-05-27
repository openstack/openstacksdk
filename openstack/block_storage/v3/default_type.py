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


class DefaultType(resource.Resource):
    resource_key = "default_type"
    resources_key = "default_types"
    base_path = "/default-types"

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_list = True

    # Create and update use the same PUT API
    create_requires_id = True
    create_method = 'PUT'

    _max_microversion = "3.67"

    # Properties
    #: The UUID of the project.
    project_id = resource.Body("project_id")
    #: The UUID for an existing volume type.
    volume_type_id = resource.Body("volume_type_id")

    def _prepare_request_body(
        self,
        patch,
        prepend_key,
        *,
        resource_request_key=None,
    ):
        body = self._body.dirty
        # Set operation expects volume_type instead of
        # volume_type_id
        if body.get('volume_type_id'):
            body['volume_type'] = body.pop('volume_type_id')
        # When setting a default type, we want the ID to be
        # appended in URL but not in the request body
        if body.get('id'):
            body.pop('id')
        body = {self.resource_key: body}
        return body
