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


class ServerRemoteConsole(resource.Resource):
    resource_key = 'remote_console'
    base_path = '/servers/%(server_id)s/remote-consoles'

    # capabilities
    allow_create = True
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = False

    _max_microversion = '2.8'

    #: Protocol of the remote console.
    protocol = resource.Body('protocol')
    #: Type of the remote console.
    type = resource.Body('type')
    #: URL used to connect to the console.
    url = resource.Body('url')
    #: The ID for the server.
    server_id = resource.URI('server_id')
