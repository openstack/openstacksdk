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

import time

from openstack.compute import compute_service
from openstack.compute.v2 import flavor
from openstack.compute.v2 import image
from openstack.compute.v2 import server_ip
from openstack import exceptions
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

    put_update = True

    # Properties
    access_ipv4 = resource.prop('accessIPv4')
    access_ipv6 = resource.prop('accessIPv6')
    #: A dictionary of addresses this server can be accessed through.
    #: The dictionary contains keys such as ``private`` and ``public``,
    #: each containing a list of dictionaries for addresses of that type.
    #: The addresses are contained in a dictionary with keys ``addr``
    #: and ``version``, which is either 4 or 6 depending on the protocol
    #: of the IP address. *Type: dict*
    addresses = resource.prop('addresses', type=dict)
    #: Timestamp of when the server was created.
    created = resource.prop('created')
    #: A dictionary with details on the flavor this server is running.
    #: The dictionary includes a key for the ``id`` of the flavor, as well
    #: as a ``links`` key, which includes a list of relevant links for this
    #: flavor. *Type: dict*
    flavor = resource.prop('flavorRef', alias='flavor', type=flavor.Flavor)
    #: An ID representing the host of this server.
    host_id = resource.prop('hostId')
    #: A dictionary with details on the image this server is running.
    #: The dictionary includes a key for ``id`` of the image, as well
    #: as a ``links`` key, which includes a list of relevant links for this
    #: image. *Type: dict*
    image = resource.prop('imageRef', alias='image', type=image.Image)
    #: A list of dictionaries holding links relevant to this server.
    links = resource.prop('links')
    #: Metadata stored for this server. *Type: dict*
    metadata = resource.prop('metadata', type=dict)
    #: The name of this server.
    name = resource.prop('name')
    #: While the server is building, this value represents the percentage
    #: of completion. Once it is completed, it will be 100.  *Type: int*
    progress = resource.prop('progress', type=int)
    #: The project this server is associated with.
    project_id = resource.prop('tenant_id')
    #: The state this server is in. Valid values include ``ACTIVE``,
    #: ``BUILDING``, ``DELETED``, ``ERROR``, ``HARD_REBOOT``, ``PASSWORD``,
    #: ``PAUSED``, ``REBOOT``, ``REBUILD``, ``RESCUED``, ``RESIZED``,
    #: ``REVERT_RESIZE``, ``SHUTOFF``, ``SOFT_DELETED``, ``STOPPED``,
    #: ``SUSPENDED``, ``UNKNOWN``, or ``VERIFY_RESIZE``.
    status = resource.prop('status')
    #: Timestamp of when this server was last updated.
    updated = resource.prop('updated')
    #: The user ID associated with this server.
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

    def wait_for_status(self, session, status='ACTIVE', failures=None,
                        interval=5, wait=120):
        """Wait for the server to be in some status.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param status: Desired status of the server.
        :param list failures: Statuses that would indicate the transition
                              failed such as 'ERROR'.
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for transition.

        :return: Method returns self on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` transition
                 to status failed to occur in wait seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` resource
                 transitioned to one of the failure states.
        """
        try:
            if self.status == status:
                return self
        except AttributeError:
            pass
        total_sleep = 0
        if failures is None:
            failures = []
        while total_sleep < wait:
            self.get(session)
            if self.status == status:
                return self
            if self.status in failures:
                msg = ("Resource %s transitioned to failure state %s" %
                       (self.id, self.status))
                raise exceptions.ResourceFailure(msg)
            time.sleep(interval)
            total_sleep += interval
        msg = "Timeout waiting for %s to transition to %s" % (self.id, status)
        raise exceptions.ResourceTimeout(msg)

    def get_floating_ips(self):
        """Get the floating ips associated with this server."""
        addresses = self.addresses[self.name]
        result = []
        for address in addresses:
            if address['OS-EXT-IPS:type'] == 'floating':
                result.append(address['addr'])
        return result


class ServerDetail(Server):
    base_path = '/servers/detail'

    # capabilities
    allow_create = False
    allow_retrieve = False
    allow_update = False
    allow_delete = False
    allow_list = True
