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

from keystoneauth1 import adapter

from openstack import resource
from openstack import utils

CONSOLE_TYPE_PROTOCOL_MAPPING = {
    'novnc': 'vnc',
    'xvpvnc': 'vnc',
    'spice-html5': 'spice',
    'spice-direct': 'spice',
    'rdp-html5': 'rdp',
    'serial': 'serial',
    'webmks': 'mks',
}


class ServerRemoteConsole(resource.Resource):
    resource_key = 'remote_console'
    base_path = '/servers/%(server_id)s/remote-consoles'

    # capabilities
    allow_create = True
    allow_fetch = False
    allow_commit = False
    allow_delete = False
    allow_list = False

    _max_microversion = '2.99'

    #: Protocol of the remote console.
    protocol = resource.Body('protocol')
    #: Type of the remote console.
    type = resource.Body('type')
    #: URL used to connect to the console.
    url = resource.Body('url')
    #: The ID for the server.
    server_id = resource.URI('server_id')

    @classmethod
    def _transform_create_request(
        cls,
        session: adapter.Adapter,
        request: resource._Request,
        *,
        microversion: str | None,
    ) -> resource._Request:
        assert isinstance(request.body, dict)  # narrow type
        body = request.body.get('remote_console', {})
        if not body.get('protocol') and body.get('type'):
            body['protocol'] = CONSOLE_TYPE_PROTOCOL_MAPPING.get(body['type'])
        if body.get('type') == 'webmks' and not utils.supports_microversion(
            session, '2.8'
        ):
            raise ValueError(
                'Console type webmks is not supported on server side'
            )
        if body.get(
            'type'
        ) == 'spice-direct' and not utils.supports_microversion(
            session, '2.99'
        ):
            raise ValueError(
                'Console type spice-direct is not supported on server side'
            )
        return request
