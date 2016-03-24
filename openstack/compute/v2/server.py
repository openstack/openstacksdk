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
from openstack.compute.v2 import metadata
from openstack import resource2
from openstack import utils


class Server(resource2.Resource, metadata.MetadataMixin):
    resource_key = 'server'
    resources_key = 'servers'
    base_path = '/servers'
    service = compute_service.ComputeService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource2.QueryParameters("image", "flavor", "name",
                                               "status", "host",
                                               changes_since="changes-since")

    #: A list of dictionaries holding links relevant to this server.
    links = resource2.Body('links')

    access_ipv4 = resource2.Body('accessIPv4')
    access_ipv6 = resource2.Body('accessIPv6')
    #: A dictionary of addresses this server can be accessed through.
    #: The dictionary contains keys such as ``private`` and ``public``,
    #: each containing a list of dictionaries for addresses of that type.
    #: The addresses are contained in a dictionary with keys ``addr``
    #: and ``version``, which is either 4 or 6 depending on the protocol
    #: of the IP address. *Type: dict*
    addresses = resource2.Body('addresses', type=dict)
    #: Timestamp of when the server was created.
    created_at = resource2.Body('created')
    #: The flavor reference, as a ID or full URL, for the flavor to use for
    #: this server.
    flavor_id = resource2.Body('flavorRef')
    #: An ID representing the host of this server.
    host_id = resource2.Body('hostId')
    #: The image reference, as a ID or full URL, for the image to use for
    #: this server.
    image_id = resource2.Body('imageRef')
    #: Metadata stored for this server. *Type: dict*
    metadata = resource2.Body('metadata', type=dict)
    #: While the server is building, this value represents the percentage
    #: of completion. Once it is completed, it will be 100.  *Type: int*
    progress = resource2.Body('progress', type=int)
    #: The ID of the project this server is associated with.
    project_id = resource2.Body('tenant_id')
    #: The state this server is in. Valid values include ``ACTIVE``,
    #: ``BUILDING``, ``DELETED``, ``ERROR``, ``HARD_REBOOT``, ``PASSWORD``,
    #: ``PAUSED``, ``REBOOT``, ``REBUILD``, ``RESCUED``, ``RESIZED``,
    #: ``REVERT_RESIZE``, ``SHUTOFF``, ``SOFT_DELETED``, ``STOPPED``,
    #: ``SUSPENDED``, ``UNKNOWN``, or ``VERIFY_RESIZE``.
    status = resource2.Body('status')
    #: Timestamp of when this server was last updated.
    updated_at = resource2.Body('updated')
    #: The ID of the owners of this server.
    user_id = resource2.Body('user_id')
    #: The name of an associated keypair
    key_name = resource2.Body('key_name')
    #: The disk configuration. Either AUTO or MANUAL.
    disk_config = resource2.Body('OS-DCF:diskConfig')
    #: The name of the availability zone this server is a part of.
    availability_zone = resource2.Body('OS-EXT-AZ:availability_zone')
    #: The power state of this server.
    power_state = resource2.Body('OS-EXT-STS:power_state')
    #: The task state of this server.
    task_state = resource2.Body('OS-EXT-STS:task_state')
    #: The VM state of this server.
    vm_state = resource2.Body('OS-EXT-STS:vm_state')
    #: A list of an attached volumes. Each item in the list contains at least
    #: an "id" key to identify the specific volumes.
    attached_volumes = resource2.Body(
        'os-extended-volumes:volumes_attached')
    #: The timestamp when the server was launched.
    launched_at = resource2.Body('OS-SRV-USG:launched_at')
    #: The timestamp when the server was terminated (if it has been).
    terminated_at = resource2.Body('OS-SRV-USG:terminated_at')
    #: A list of applicable security groups. Each group contains keys for
    #: description, name, id, and rules.
    security_groups = resource2.Body('security_groups')
    #: When a server is first created, it provides the administrator password.
    admin_password = resource2.Body('adminPass')
    #: The file path and contents, text only, to inject into the server at
    #: launch. The maximum size of the file path data is 255 bytes.
    #: The maximum limit is The number of allowed bytes in the decoded,
    #: rather than encoded, data.
    personality = resource2.Body('personality')
    #: Configuration information or scripts to use upon launch.
    #: Must be Base64 encoded.
    user_data = resource2.Body('user_data')
    #: Enables fine grained control of the block device mapping for an
    #: instance. This is typically used for booting servers from volumes.
    block_device_mapping = resource2.Body('block_device_mapping_v2', type=dict)
    #: The dictionary of data to send to the scheduler.
    scheduler_hints = resource2.Body('os:scheduler_hints', type=dict)
    #: A networks object. Required parameter when there are multiple
    #: networks defined for the tenant. When you do not specify the
    #: networks parameter, the server attaches to the only network
    #: created for the current tenant.
    networks = resource2.Body('networks', type=dict)

    def _action(self, session, body):
        """Preform server actions given the message body."""
        # NOTE: This is using Server.base_path instead of self.base_path
        # as both Server and ServerDetail instances can be acted on, but
        # the URL used is sans any additional /detail/ part.
        url = utils.urljoin(Server.base_path, self.id, 'action')
        headers = {'Accept': ''}
        return session.post(
            url, endpoint_filter=self.service, json=body, headers=headers)

    def change_password(self, session, new_password):
        """Change the administrator password to the given password."""
        body = {'changePassword': {'adminPass': new_password}}
        self._action(session, body)

    def reboot(self, session, reboot_type):
        """Reboot server where reboot_type might be 'SOFT' or 'HARD'."""
        body = {'reboot': {'type': reboot_type}}
        self._action(session, body)

    def rebuild(self, session, name, admin_password,
                preserve_ephemeral=False, image=None,
                access_ipv4=None, access_ipv6=None,
                metadata=None, personality=None):
        """Rebuild the server with the given arguments."""
        action = {
            'name': name,
            'adminPass': admin_password,
            'preserve_ephemeral': preserve_ephemeral
        }
        if image is not None:
            action['imageRef'] = resource2.Resource._get_id(image)
        if access_ipv4 is not None:
            action['accessIPv4'] = access_ipv4
        if access_ipv6 is not None:
            action['accessIPv6'] = access_ipv6
        if metadata is not None:
            action['metadata'] = metadata
        if personality is not None:
            action['personality'] = personality

        body = {'rebuild': action}
        response = self._action(session, body)
        self._translate_response(response)
        return self

    def resize(self, session, flavor):
        """Resize server to flavor reference."""
        body = {'resize': {'flavorRef': flavor}}
        self._action(session, body)

    def confirm_resize(self, session):
        """Confirm the resize of the server."""
        body = {'confirmResize': None}
        self._action(session, body)

    def revert_resize(self, session):
        """Revert the resize of the server."""
        body = {'revertResize': None}
        self._action(session, body)

    def create_image(self, session, name, metadata=None):
        """Create image from server."""
        action = {'name': name}
        if metadata is not None:
            action['metadata'] = metadata
        body = {'createImage': action}
        self._action(session, body)

    def add_security_group(self, session, security_group):
        body = {"addSecurityGroup": {"name": security_group}}
        self._action(session, body)

    def remove_security_group(self, session, security_group):
        body = {"removeSecurityGroup": {"name": security_group}}
        self._action(session, body)


class ServerDetail(Server):
    base_path = '/servers/detail'

    # capabilities
    allow_create = False
    allow_get = False
    allow_update = False
    allow_delete = False
    allow_list = True
