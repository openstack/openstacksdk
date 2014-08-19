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

from openstack.compute import compute_service
from openstack.compute.v2 import server_ip
from openstack import resource
from openstack import utils


class Server(resource.Resource):
    resource_key = 'server'
    resources_key = 'servers'
    base_path = '/servers'
    service = compute_service.ComputeService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    access_ipv4 = resource.prop('accessIPv4')
    access_ipv6 = resource.prop('accessIPv6')
    addresses = resource.prop('addresses', type=dict)
    created = resource.prop('created')
    flavor = resource.prop('flavor', type=dict)
    host_id = resource.prop('hostId')
    image = resource.prop('image', type=dict)
    links = resource.prop('links')
    metadata = resource.prop('metadata')
    name = resource.prop('name')
    progress = resource.prop('progress', type=int)
    project_id = resource.prop('tenant_id')
    status = resource.prop('status')
    updated = resource.prop('updated')
    user_id = resource.prop('user_id')

    def ips(self, session):
        """Get server IPs."""
        path_args = {'server_id': self.id}
        return server_ip.ServerIP.list(session, path_args=path_args)

    def action(self, session, body):
        """Preform server actions given the message body."""
        url = utils.urljoin(self.base_path, self.id, 'action')
        resp = session.put(url, service=self.service, json=body).body
        return resp

    def change_password(self, session, new_password):
        """Change the administrator password to the given password."""
        body = {'changePassword': {'adminPass': new_password}}
        return self.action(session, body)

    def reboot(self, session, reboot_type):
        """Reboot server where reboot_type might be 'SOFT' or 'HARD'."""
        body = {'reboot': {'type': reboot_type}}
        return self.action(session, body)

    def rebuild(self, session, name, image_href, admin_password,
                access_ipv4=None, access_ipv6=None,
                metadata=None, personality=None):
        """Rebuild the server with the given arguments."""
        action = {
            'name': name,
            'adminPass': admin_password,
            'imageRef': image_href,
        }
        if access_ipv4 is not None:
            action['accessIPv4'] = access_ipv4
        if access_ipv6 is not None:
            action['accessIPv6'] = access_ipv6
        if metadata is not None:
            action['metadata'] = metadata
        if personality is not None:
            action['personality'] = personality
        body = {'rebuild': action}
        return self.action(session, body)

    def resize(self, session, flavor):
        """Resize server to flavor reference."""
        body = {'resize': {'flavorRef': flavor}}
        return self.action(session, body)

    def confirm_resize(self, session):
        """Confirm the resize of the server."""
        body = {'confirmResize': None}
        return self.action(session, body)

    def revert_resize(self, session):
        """Revert the resize of the server."""
        body = {'revertResize': None}
        return self.action(session, body)

    def create_image(self, session, name, metadata=None):
        """Create image from server."""
        action = {'name': name}
        if metadata is not None:
            action['metadata'] = metadata
        body = {'createImage': action}
        return self.action(session, body)
