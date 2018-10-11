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


class Policy(resource.Resource):
    resource_key = 'policy'
    resources_key = 'policies'
    base_path = '/policies'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'

    # Properties
    #: The policy rule set itself, as a serialized blob. *Type: string*
    blob = resource.Body('blob')
    #: The links for the policy resource.
    links = resource.Body('links')
    #: The ID for the project.
    project_id = resource.Body('project_id')
    #: The MIME Media Type of the serialized policy blob. *Type: string*
    type = resource.Body('type')
    #: The ID of the user who owns the policy
    user_id = resource.Body('user_id')
