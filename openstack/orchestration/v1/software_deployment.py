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


class SoftwareDeployment(resource.Resource):
    resource_key = 'software_deployment'
    resources_key = 'software_deployments'
    base_path = '/software_deployments'

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True
    allow_commit = True

    # Properties
    #: The stack action that triggers this deployment resource.
    action = resource.Body('action')
    #: The UUID of the software config resource that runs when applying to the
    #: server.
    config_id = resource.Body('config_id')
    #: A map containing the names and values of all inputs to the config.
    input_values = resource.Body('input_values', type=dict)
    #: A map containing the names and values from the deployment.
    output_values = resource.Body('output_values', type=dict)
    #: The UUID of the compute server to which the configuration applies.
    server_id = resource.Body('server_id')
    #: The ID of the authentication project which can also perform operations
    #: on this deployment.
    stack_user_project_id = resource.Body('stack_user_project_id')
    #: Current status of the software deployment.
    status = resource.Body('status')
    #: Error description for the last status change.
    status_reason = resource.Body('status_reason')
    #: The date and time when the software deployment resource was created.
    created_at = resource.Body('creation_time')
    #: The date and time when the software deployment resource was created.
    updated_at = resource.Body('updated_time')

    def create(self, session):
        # This overrides the default behavior of resource creation because
        # heat doesn't accept resource_key in its request.
        return super(SoftwareDeployment, self).create(
            session, prepend_key=False)

    def commit(self, session):
        # This overrides the default behavior of resource creation because
        # heat doesn't accept resource_key in its request.
        return super(SoftwareDeployment, self).commit(
            session, prepend_key=False)
