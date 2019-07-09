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

from openstack.compute.v2 import metadata
from openstack.image.v2 import image
from openstack import exceptions
from openstack import resource
from openstack import utils


class Server(resource.Resource, metadata.MetadataMixin, resource.TagMixin):
    resource_key = 'server'
    resources_key = 'servers'
    base_path = '/servers'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        "auto_disk_config", "availability_zone",
        "created_at", "description", "flavor",
        "hostname", "image", "kernel_id", "key_name",
        "launch_index", "launched_at", "locked_by", "name",
        "node", "power_state", "progress", "project_id", "ramdisk_id",
        "reservation_id", "root_device_name",
        "status", "task_state", "terminated_at", "user_id",
        "vm_state",
        "sort_key", "sort_dir",
        access_ipv4="access_ip_v4",
        access_ipv6="access_ip_v6",
        has_config_drive="config_drive",
        deleted_only="deleted",
        compute_host="host",
        is_soft_deleted="soft_deleted",
        ipv4_address="ip",
        ipv6_address="ip6",
        changes_since="changes-since",
        changes_before="changes-before",
        id="uuid",
        all_projects="all_tenants",
        **resource.TagMixin._tag_query_parameters
    )

    _max_microversion = '2.72'

    #: A list of dictionaries holding links relevant to this server.
    links = resource.Body('links')

    access_ipv4 = resource.Body('accessIPv4')
    access_ipv6 = resource.Body('accessIPv6')
    #: A dictionary of addresses this server can be accessed through.
    #: The dictionary contains keys such as ``private`` and ``public``,
    #: each containing a list of dictionaries for addresses of that type.
    #: The addresses are contained in a dictionary with keys ``addr``
    #: and ``version``, which is either 4 or 6 depending on the protocol
    #: of the IP address. *Type: dict*
    addresses = resource.Body('addresses', type=dict)
    #: When a server is first created, it provides the administrator password.
    admin_password = resource.Body('adminPass')
    #: A list of an attached volumes. Each item in the list contains at least
    #: an "id" key to identify the specific volumes.
    attached_volumes = resource.Body(
        'os-extended-volumes:volumes_attached')
    #: The name of the availability zone this server is a part of.
    availability_zone = resource.Body('OS-EXT-AZ:availability_zone')
    #: Enables fine grained control of the block device mapping for an
    #: instance. This is typically used for booting servers from volumes.
    block_device_mapping = resource.Body('block_device_mapping_v2')
    #: Indicates whether or not a config drive was used for this server.
    config_drive = resource.Body('config_drive')
    #: The name of the compute host on which this instance is running.
    #: Appears in the response for administrative users only.
    compute_host = resource.Body('OS-EXT-SRV-ATTR:host')
    #: Timestamp of when the server was created.
    created_at = resource.Body('created')
    #: The description of the server. Before microversion
    #: 2.19 this was set to the server name.
    description = resource.Body('description')
    #: The disk configuration. Either AUTO or MANUAL.
    disk_config = resource.Body('OS-DCF:diskConfig')
    #: The flavor reference, as a ID or full URL, for the flavor to use for
    #: this server.
    flavor_id = resource.Body('flavorRef')
    #: The flavor property as returned from server.
    # TODO(gtema): replace with flavor.Flavor addressing flavor.original_name
    flavor = resource.Body('flavor', type=dict)
    #: Indicates whether a configuration drive enables metadata injection.
    #: Not all cloud providers enable this feature.
    has_config_drive = resource.Body('config_drive')
    #: An ID representing the host of this server.
    host_id = resource.Body('hostId')
    #: The host status.
    host_status = resource.Body('host_status')
    #: The hostname set on the instance when it is booted.
    #: By default, it appears in the response for administrative users only.
    hostname = resource.Body('OS-EXT-SRV-ATTR:hostname')
    #: The hypervisor host name. Appears in the response for administrative
    #: users only.
    hypervisor_hostname = resource.Body('OS-EXT-SRV-ATTR:hypervisor_hostname')
    #: The image reference, as a ID or full URL, for the image to use for
    #: this server.
    image_id = resource.Body('imageRef')
    #: The image property as returned from server.
    image = resource.Body('image', type=image.Image)
    #: The instance name. The Compute API generates the instance name from the
    #: instance name template. Appears in the response for administrative users
    #: only.
    instance_name = resource.Body('OS-EXT-SRV-ATTR:instance_name')
    # The locked status of the server
    is_locked = resource.Body('locked', type=bool)
    #: The UUID of the kernel image when using an AMI. Will be null if not.
    #: By default, it appears in the response for administrative users only.
    kernel_id = resource.Body('OS-EXT-SRV-ATTR:kernel_id')
    #: The name of an associated keypair
    key_name = resource.Body('key_name')
    #: When servers are launched via multiple create, this is the
    #: sequence in which the servers were launched. By default, it
    #: appears in the response for administrative users only.
    launch_index = resource.Body('OS-EXT-SRV-ATTR:launch_index', type=int)
    #: The timestamp when the server was launched.
    launched_at = resource.Body('OS-SRV-USG:launched_at')
    #: Metadata stored for this server. *Type: dict*
    metadata = resource.Body('metadata', type=dict)
    #: A networks object. Required parameter when there are multiple
    #: networks defined for the tenant. When you do not specify the
    #: networks parameter, the server attaches to the only network
    #: created for the current tenant.
    networks = resource.Body('networks')
    #: The file path and contents, text only, to inject into the server at
    #: launch. The maximum size of the file path data is 255 bytes.
    #: The maximum limit is The number of allowed bytes in the decoded,
    #: rather than encoded, data.
    personality = resource.Body('personality')
    #: The power state of this server.
    power_state = resource.Body('OS-EXT-STS:power_state')
    #: While the server is building, this value represents the percentage
    #: of completion. Once it is completed, it will be 100.  *Type: int*
    progress = resource.Body('progress', type=int)
    #: The ID of the project this server is associated with.
    project_id = resource.Body('tenant_id')
    #: The UUID of the ramdisk image when using an AMI. Will be null if not.
    #: By default, it appears in the response for administrative users only.
    ramdisk_id = resource.Body('OS-EXT-SRV-ATTR:ramdisk_id')
    #: The reservation id for the server. This is an id that can be
    #: useful in tracking groups of servers created with multiple create,
    #: that will all have the same reservation_id. By default, it appears
    #: in the response for administrative users only.
    reservation_id = resource.Body('OS-EXT-SRV-ATTR:reservation_id')
    #: The root device name for the instance By default, it appears in the
    #: response for administrative users only.
    root_device_name = resource.Body('OS-EXT-SRV-ATTR:root_device_name')
    #: The dictionary of data to send to the scheduler.
    scheduler_hints = resource.Body('OS-SCH-HNT:scheduler_hints', type=dict)
    #: A list of applicable security groups. Each group contains keys for
    #: description, name, id, and rules.
    security_groups = resource.Body('security_groups',
                                    type=list, list_type=dict)
    #: The UUIDs of the server groups to which the server belongs.
    #: Currently this can contain at most one entry.
    server_groups = resource.Body('server_groups', type=list, list_type=dict)
    #: The state this server is in. Valid values include ``ACTIVE``,
    #: ``BUILDING``, ``DELETED``, ``ERROR``, ``HARD_REBOOT``, ``PASSWORD``,
    #: ``PAUSED``, ``REBOOT``, ``REBUILD``, ``RESCUED``, ``RESIZED``,
    #: ``REVERT_RESIZE``, ``SHUTOFF``, ``SOFT_DELETED``, ``STOPPED``,
    #: ``SUSPENDED``, ``UNKNOWN``, or ``VERIFY_RESIZE``.
    status = resource.Body('status')
    #: The task state of this server.
    task_state = resource.Body('OS-EXT-STS:task_state')
    #: The timestamp when the server was terminated (if it has been).
    terminated_at = resource.Body('OS-SRV-USG:terminated_at')
    #: A list of trusted certificate IDs, that were used during image
    #: signature verification to verify the signing certificate.
    trusted_image_certificates = resource.Body(
        'trusted_image_certificates', type=list)
    #: Timestamp of when this server was last updated.
    updated_at = resource.Body('updated')
    #: Configuration information or scripts to use upon launch.
    #: Must be Base64 encoded.
    user_data = resource.Body('OS-EXT-SRV-ATTR:user_data')
    #: The ID of the owners of this server.
    user_id = resource.Body('user_id')
    #: The VM state of this server.
    vm_state = resource.Body('OS-EXT-STS:vm_state')

    def _prepare_request(self, requires_id=True, prepend_key=True,
                         base_path=None):
        request = super(Server, self)._prepare_request(requires_id=requires_id,
                                                       prepend_key=prepend_key,
                                                       base_path=base_path)

        server_body = request.body[self.resource_key]

        # Some names exist without prefix on requests but with a prefix
        # on responses. If we find that we've populated one of these
        # attributes with something and then go to make a request, swap out
        # the name to the bare version.

        # Availability Zones exist with a prefix on response, but not request
        az_key = "OS-EXT-AZ:availability_zone"
        if az_key in server_body:
            server_body["availability_zone"] = server_body.pop(az_key)

        # User Data exists with a prefix on response, but not request
        ud_key = "OS-EXT-SRV-ATTR:user_data"
        if ud_key in server_body:
            server_body["user_data"] = server_body.pop(ud_key)

        # Scheduler hints are sent in a top-level scope, not within the
        # resource_key scope like everything else. If we try to send
        # scheduler_hints, pop them out of the resource_key scope and into
        # their own top-level scope.
        hint_key = "OS-SCH-HNT:scheduler_hints"
        if hint_key in server_body:
            request.body[hint_key] = server_body.pop(hint_key)

        return request

    def _action(self, session, body, microversion=None):
        """Preform server actions given the message body."""
        # NOTE: This is using Server.base_path instead of self.base_path
        # as both Server and ServerDetail instances can be acted on, but
        # the URL used is sans any additional /detail/ part.
        url = utils.urljoin(Server.base_path, self.id, 'action')
        headers = {'Accept': ''}
        response = session.post(
            url, json=body, headers=headers, microversion=microversion)
        exceptions.raise_from_response(response)
        return response

    def change_password(self, session, new_password):
        """Change the administrator password to the given password."""
        body = {'changePassword': {'adminPass': new_password}}
        self._action(session, body)

    def get_password(self, session):
        """Get the encrypted administrator password."""
        url = utils.urljoin(Server.base_path, self.id, 'os-server-password')
        return session.get(url)

    def reboot(self, session, reboot_type):
        """Reboot server where reboot_type might be 'SOFT' or 'HARD'."""
        body = {'reboot': {'type': reboot_type}}
        self._action(session, body)

    def force_delete(self, session):
        """Force delete a server."""
        body = {'forceDelete': None}
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
            action['imageRef'] = resource.Resource._get_id(image)
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

        # You won't believe it - wait, who am I kidding - of course you will!
        # Nova returns the URL of the image created in the Location
        # header of the response. (what?) But, even better, the URL it responds
        # with has a very good chance of being wrong (it is built from
        # nova.conf values that point to internal API servers in any cloud
        # large enough to have both public and internal endpoints.
        # However, nobody has ever noticed this because novaclient doesn't
        # actually use that URL - it extracts the id from the end of
        # the url, then returns the id. This leads us to question:
        #   a) why Nova is going to return a value in a header
        #   b) why it's going to return data that probably broken
        #   c) indeed the very nature of the fabric of reality
        # Although it fills us with existential dread, we have no choice but
        # to follow suit like a lemming being forced over a cliff by evil
        # producers from Disney.
        microversion = None
        if utils.supports_microversion(session, '2.45'):
            microversion = '2.45'
        response = self._action(session, body, microversion)

        body = None
        try:
            # There might be body, might be not
            body = response.json()
        except Exception:
            pass
        if body and 'image_id' in body:
            image_id = body['image_id']
        else:
            image_id = response.headers['Location'].rsplit('/', 1)[1]

        return image_id

    def add_security_group(self, session, security_group_name):
        body = {"addSecurityGroup": {"name": security_group_name}}
        self._action(session, body)

    def remove_security_group(self, session, security_group_name):
        body = {"removeSecurityGroup": {"name": security_group_name}}
        self._action(session, body)

    def reset_state(self, session, state):
        body = {"os-resetState": {"state": state}}
        self._action(session, body)

    def add_fixed_ip(self, session, network_id):
        body = {"addFixedIp": {"networkId": network_id}}
        self._action(session, body)

    def remove_fixed_ip(self, session, address):
        body = {"removeFixedIp": {"address": address}}
        self._action(session, body)

    def add_floating_ip(self, session, address, fixed_address=None):
        body = {"addFloatingIp": {"address": address}}
        if fixed_address is not None:
            body['addFloatingIp']['fixed_address'] = fixed_address
        self._action(session, body)

    def remove_floating_ip(self, session, address):
        body = {"removeFloatingIp": {"address": address}}
        self._action(session, body)

    def backup(self, session, name, backup_type, rotation):
        body = {
            "createBackup": {
                "name": name,
                "backup_type": backup_type,
                "rotation": rotation
            }
        }
        self._action(session, body)

    def pause(self, session):
        body = {"pause": None}
        self._action(session, body)

    def unpause(self, session):
        body = {"unpause": None}
        self._action(session, body)

    def suspend(self, session):
        body = {"suspend": None}
        self._action(session, body)

    def resume(self, session):
        body = {"resume": None}
        self._action(session, body)

    def lock(self, session):
        body = {"lock": None}
        self._action(session, body)

    def unlock(self, session):
        body = {"unlock": None}
        self._action(session, body)

    def rescue(self, session, admin_pass=None, image_ref=None):
        body = {"rescue": {}}
        if admin_pass is not None:
            body["rescue"]["adminPass"] = admin_pass
        if image_ref is not None:
            body["rescue"]["rescue_image_ref"] = image_ref
        self._action(session, body)

    def unrescue(self, session):
        body = {"unrescue": None}
        self._action(session, body)

    def evacuate(self, session, host=None, admin_pass=None, force=None):
        body = {"evacuate": {}}
        if host is not None:
            body["evacuate"]["host"] = host
        if admin_pass is not None:
            body["evacuate"]["adminPass"] = admin_pass
        if force is not None:
            body["evacuate"]["force"] = force
        self._action(session, body)

    def start(self, session):
        body = {"os-start": None}
        self._action(session, body)

    def stop(self, session):
        body = {"os-stop": None}
        self._action(session, body)

    def shelve(self, session):
        body = {"shelve": None}
        self._action(session, body)

    def unshelve(self, session):
        body = {"unshelve": None}
        self._action(session, body)

    def migrate(self, session):
        body = {"migrate": None}
        self._action(session, body)

    def get_console_output(self, session, length=None):
        body = {"os-getConsoleOutput": {}}
        if length is not None:
            body["os-getConsoleOutput"]["length"] = length
        resp = self._action(session, body)
        return resp.json()

    def live_migrate(self, session, host, force, block_migration,
                     disk_over_commit=False):
        if utils.supports_microversion(session, '2.30'):
            return self._live_migrate_30(
                session, host,
                force=force,
                block_migration=block_migration)
        elif utils.supports_microversion(session, '2.25'):
            return self._live_migrate_25(
                session, host,
                force=force,
                block_migration=block_migration)
        else:
            return self._live_migrate(
                session, host,
                force=force,
                block_migration=block_migration,
                disk_over_commit=disk_over_commit)

    def _live_migrate_30(self, session, host, force, block_migration):
        microversion = '2.30'
        body = {'host': None}
        if block_migration is None:
            block_migration = 'auto'
        body['block_migration'] = block_migration
        if host:
            body['host'] = host
            if force:
                body['force'] = force
        self._action(
            session, {'os-migrateLive': body}, microversion=microversion)

    def _live_migrate_25(self, session, host, force, block_migration):
        microversion = '2.25'
        body = {'host': None}
        if block_migration is None:
            block_migration = 'auto'
        body['block_migration'] = block_migration
        if host:
            body['host'] = host
            if not force:
                raise ValueError(
                    "Live migration on this cloud implies 'force'"
                    " if the 'host' option has been given and it is not"
                    " possible to disable. It is recommended to not use 'host'"
                    " at all on this cloud as it is inherently unsafe, but if"
                    " it is unavoidable, please supply 'force=True' so that it"
                    " is clear you understand the risks.")
        self._action(
            session, {'os-migrateLive': body}, microversion=microversion)

    def _live_migrate(self, session, host, force, block_migration,
                      disk_over_commit):
        microversion = None
        body = {
            'host': None,
        }
        if block_migration == 'auto':
            raise ValueError(
                "Live migration on this cloud does not support 'auto' as"
                " a parameter to block_migration, but only True and False.")
        body['block_migration'] = block_migration or False
        body['disk_over_commit'] = disk_over_commit or False
        if host:
            body['host'] = host
            if not force:
                raise ValueError(
                    "Live migration on this cloud implies 'force'"
                    " if the 'host' option has been given and it is not"
                    " possible to disable. It is recommended to not use 'host'"
                    " at all on this cloud as it is inherently unsafe, but if"
                    " it is unavoidable, please supply 'force=True' so that it"
                    " is clear you understand the risks.")
        self._action(
            session, {'os-migrateLive': body}, microversion=microversion)

    def fetch_security_groups(self, session):
        """Fetch security groups of a server.

        :returns: Updated Server instance.

        """
        url = utils.urljoin(Server.base_path, self.id, 'os-security-groups')

        response = session.get(url)

        exceptions.raise_from_response(response)

        try:
            data = response.json()
            if 'security_groups' in data:
                self.security_groups = data['security_groups']
        except ValueError:
            pass

        return self


ServerDetail = Server
