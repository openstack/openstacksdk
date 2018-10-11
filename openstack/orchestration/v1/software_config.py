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


class SoftwareConfig(resource.Resource):
    resource_key = 'software_config'
    resources_key = 'software_configs'
    base_path = '/software_configs'

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True
    allow_commit = False

    # Properties
    #: Configuration script or manifest that defines which configuration is
    #: performed
    config = resource.Body('config')
    #: The date and time when the software config resource was created.
    created_at = resource.Body('creation_time')
    #: A string indicating the namespace used for grouping software configs.
    group = resource.Body('group')
    #: A list of schemas each representing an input this software config
    #: expects.
    inputs = resource.Body('inputs')
    #: Name of the software config.
    name = resource.Body('name')
    #: A string that contains options that are specific to the configuraiton
    #: management tool that this resource uses.
    options = resource.Body('options')
    #: A list of schemas each representing an output this software config
    #: produces.
    outputs = resource.Body('outputs')

    def create(self, session):
        # This overrides the default behavior of resource creation because
        # heat doesn't accept resource_key in its request.
        return super(SoftwareConfig, self).create(session, prepend_key=False)
