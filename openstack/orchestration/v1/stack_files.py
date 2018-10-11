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


class StackFiles(resource.Resource):

    base_path = "/stacks/%(stack_name)s/%(stack_id)s/files"

    # capabilities
    allow_create = False
    allow_list = False
    allow_fetch = True
    allow_delete = False
    allow_commit = False

    # Properties
    #: Name of the stack where the template is referenced.
    name = resource.URI('stack_name')
    # Backwards compat
    stack_name = name
    #: ID of the stack where the template is referenced.
    id = resource.URI('stack_id')
    # Backwards compat
    stack_id = id

    def fetch(self, session):
        # The stack files response contains a map of filenames and file
        # contents.
        request = self._prepare_request(requires_id=False)
        resp = session.get(request.url)
        return resp.json()
