# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import types so that we can reference ListType in sphinx param declarations.
# We can't just use list, because sphinx gets confused by
# openstack.resource.Resource.list and openstack.resource2.Resource.list
import base64
import datetime
import functools
import iso8601
import operator
import threading
import time
import types  # noqa

from openstack.cloud import exc
from openstack.cloud import meta
from openstack.cloud import _normalize
from openstack.cloud import _utils
from openstack import exceptions
from openstack import proxy
from openstack import utils


class ComputeCloudMixin(_normalize.Normalizer):

    def __init__(self):
        self._servers = None
        self._servers_time = 0
        self._servers_lock = threading.Lock()

    @property
    def _compute_region(self):
        # This is only used in exception messages. Can we get rid of it?
        return self.config.get_region_name('compute')

    def get_flavor_name(self, flavor_id):
        flavor = self.get_flavor(flavor_id, get_extra=False)
        if flavor:
            return flavor['name']
        return None

    def get_flavor_by_ram(self, ram, include=None, get_extra=True):
        """Get a flavor based on amount of RAM available.

        Finds the flavor with the least amount of RAM that is at least
        as much as the specified amount. If `include` is given, further
        filter based on matching flavor name.

        :param int ram: Minimum amount of RAM.
        :param string include: If given, will return a flavor whose name
            contains this string as a substring.
        """
        flavors = self.list_flavors(get_extra=get_extra)
        for flavor in sorted(flavors, key=operator.itemgetter('ram')):
            if (flavor['ram'] >= ram
                    and (not include or include in flavor['name'])):
                return flavor
        raise exc.OpenStackCloudException(
            "Could not find a flavor with {ram} and '{include}'".format(
                ram=ram, include=include))

    @_utils.cache_on_arguments()
    def _nova_extensions(self):
        extensions = set()
        data = proxy._json_response(
            self.compute.get('/extensions'),
            error_message="Error fetching extension list for nova")

        for extension in self._get_and_munchify('extensions', data):
            extensions.add(extension['alias'])
        return extensions

    def _has_nova_extension(self, extension_name):
        return extension_name in self._nova_extensions()

    def search_keypairs(self, name_or_id=None, filters=None):
        keypairs = self.list_keypairs(
            filters=filters if isinstance(filters, dict) else None
        )
        return _utils._filter_list(keypairs, name_or_id, filters)

    def search_flavors(self, name_or_id=None, filters=None, get_extra=True):
        flavors = self.list_flavors(get_extra=get_extra)
        return _utils._filter_list(flavors, name_or_id, filters)

    def search_servers(
            self, name_or_id=None, filters=None, detailed=False,
            all_projects=False, bare=False):
        servers = self.list_servers(
            detailed=detailed, all_projects=all_projects, bare=bare)
        return _utils._filter_list(servers, name_or_id, filters)

    def search_server_groups(self, name_or_id=None, filters=None):
        """Seach server groups.

        :param name: server group name or ID.
        :param filters: a dict containing additional filters to use.

        :returns: a list of dicts containing the server groups

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        server_groups = self.list_server_groups()
        return _utils._filter_list(server_groups, name_or_id, filters)

    def list_keypairs(self, filters=None):
        """List all available keypairs.

        :returns: A list of ``munch.Munch`` containing keypair info.

        """
        if not filters:
            filters = {}
        return list(self.compute.keypairs(allow_unknown_params=True,
                                          **filters))

    @_utils.cache_on_arguments()
    def list_availability_zone_names(self, unavailable=False):
        """List names of availability zones.

        :param bool unavailable: Whether or not to include unavailable zones
                                 in the output. Defaults to False.

        :returns: A list of availability zone names, or an empty list if the
                  list could not be fetched.
        """
        try:
            zones = self.compute.availability_zones()
            ret = []
            for zone in zones:
                if zone.state['available'] or unavailable:
                    ret.append(zone.name)
            return ret
        except exceptions.SDKException:
            self.log.debug(
                "Availability zone list could not be fetched",
                exc_info=True)
            return []

    @_utils.cache_on_arguments()
    def list_flavors(self, get_extra=False):
        """List all available flavors.

        :param get_extra: Whether or not to fetch extra specs for each flavor.
                          Defaults to True. Default behavior value can be
                          overridden in clouds.yaml by setting
                          openstack.cloud.get_extra_specs to False.
        :returns: A list of flavor ``munch.Munch``.

        """
        data = self.compute.flavors(details=True)
        flavors = []

        for flavor in data:
            if not flavor.extra_specs and get_extra:
                flavor.fetch_extra_specs(self.compute)
            flavors.append(flavor._to_munch(original_names=False))
        return flavors

    def list_server_security_groups(self, server):
        """List all security groups associated with the given server.

        :returns: A list of security group ``munch.Munch``.
        """

        # Don't even try if we're a cloud that doesn't have them
        if not self._has_secgroups():
            return []

        server = self.compute.get_server(server)

        server.fetch_security_groups(self.compute)

        return self._normalize_secgroups(server.security_groups)

    def _get_server_security_groups(self, server, security_groups):
        if not self._has_secgroups():
            raise exc.OpenStackCloudUnavailableFeature(
                "Unavailable feature: security groups"
            )

        if not isinstance(server, dict):
            server = self.get_server(server, bare=True)

            if server is None:
                self.log.debug('Server %s not found', server)
                return None, None

        if not isinstance(security_groups, (list, tuple)):
            security_groups = [security_groups]

        sec_group_objs = []

        for sg in security_groups:
            if not isinstance(sg, dict):
                sg = self.get_security_group(sg)

                if sg is None:
                    self.log.debug('Security group %s not found for adding',
                                   sg)

                    return None, None

            sec_group_objs.append(sg)

        return server, sec_group_objs

    def add_server_security_groups(self, server, security_groups):
        """Add security groups to a server.

        Add existing security groups to an existing server. If the security
        groups are already present on the server this will continue unaffected.

        :returns: False if server or security groups are undefined, True
            otherwise.

        :raises: ``OpenStackCloudException``, on operation error.
        """
        server, security_groups = self._get_server_security_groups(
            server, security_groups)

        if not (server and security_groups):
            return False

        for sg in security_groups:
            self.compute.add_security_group_to_server(server, sg)

        return True

    def remove_server_security_groups(self, server, security_groups):
        """Remove security groups from a server

        Remove existing security groups from an existing server. If the
        security groups are not present on the server this will continue
        unaffected.

        :returns: False if server or security groups are undefined, True
            otherwise.

        :raises: ``OpenStackCloudException``, on operation error.
        """
        server, security_groups = self._get_server_security_groups(
            server, security_groups)

        if not (server and security_groups):
            return False

        ret = True

        for sg in security_groups:
            try:
                self.compute.remove_security_group_from_server(server, sg)

            except exceptions.ResourceNotFound:
                # NOTE(jamielennox): Is this ok? If we remove something that
                # isn't present should we just conclude job done or is that an
                # error? Nova returns ok if you try to add a group twice.
                self.log.debug(
                    "The security group %s was not present on server %s so "
                    "no action was performed", sg.name, server.name)
                ret = False

        return ret

    def list_servers(self, detailed=False, all_projects=False, bare=False,
                     filters=None):
        """List all available servers.

        :param detailed: Whether or not to add detailed additional information.
                         Defaults to False.
        :param all_projects: Whether to list servers from all projects or just
                             the current auth scoped project.
        :param bare: Whether to skip adding any additional information to the
                     server record. Defaults to False, meaning the addresses
                     dict will be populated as needed from neutron. Setting
                     to True implies detailed = False.
        :param filters: Additional query parameters passed to the API server.

        :returns: A list of server ``munch.Munch``.

        """
        # If pushdown filters are specified and we do not have batched caching
        # enabled, bypass local caching and push down the filters.
        if filters and self._SERVER_AGE == 0:
            return self._list_servers(
                detailed=detailed,
                all_projects=all_projects,
                bare=bare,
                filters=filters,
            )

        if (time.time() - self._servers_time) >= self._SERVER_AGE:
            # Since we're using cached data anyway, we don't need to
            # have more than one thread actually submit the list
            # servers task.  Let the first one submit it while holding
            # a lock, and the non-blocking acquire method will cause
            # subsequent threads to just skip this and use the old
            # data until it succeeds.
            # Initially when we never got data, block to retrieve some data.
            first_run = self._servers is None
            if self._servers_lock.acquire(first_run):
                try:
                    if not (first_run and self._servers is not None):
                        self._servers = self._list_servers(
                            detailed=detailed,
                            all_projects=all_projects,
                            bare=bare)
                        self._servers_time = time.time()
                finally:
                    self._servers_lock.release()
        # Wrap the return with filter_list so that if filters were passed
        # but we were batching/caching and thus always fetching the whole
        # list from the cloud, we still return a filtered list.
        return _utils._filter_list(self._servers, None, filters)

    def _list_servers(self, detailed=False, all_projects=False, bare=False,
                      filters=None):
        filters = filters or {}
        servers = [
            # TODO(mordred) Add original_names=False here and update the
            # normalize file for server. Then, just remove the normalize call
            # and the to_munch call.
            self._normalize_server(server._to_munch())
            for server in self.compute.servers(
                all_projects=all_projects, allow_unknown_params=True,
                **filters)]
        return [
            self._expand_server(server, detailed, bare)
            for server in servers
        ]

    def list_server_groups(self):
        """List all available server groups.

        :returns: A list of server group dicts.

        """
        return list(self.compute.server_groups())

    def get_compute_limits(self, name_or_id=None):
        """ Get compute limits for a project

        :param name_or_id: (optional) project name or ID to get limits for
                           if different from the current project
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the limits
        """
        params = {}
        project_id = None
        error_msg = "Failed to get limits"
        if name_or_id:

            proj = self.get_project(name_or_id)
            if not proj:
                raise exc.OpenStackCloudException("project does not exist")
            project_id = proj.id
            params['tenant_id'] = project_id
            error_msg = "{msg} for the project: {project} ".format(
                msg=error_msg, project=name_or_id)

        data = proxy._json_response(
            self.compute.get('/limits', params=params))
        limits = self._get_and_munchify('limits', data)
        return self._normalize_compute_limits(limits, project_id=project_id)

    def get_keypair(self, name_or_id, filters=None):
        """Get a keypair by name or ID.

        :param name_or_id: Name or ID of the keypair.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A keypair ``munch.Munch`` or None if no matching keypair is
                  found.
        """
        return _utils._get_entity(self, 'keypair', name_or_id, filters)

    def get_flavor(self, name_or_id, filters=None, get_extra=True):
        """Get a flavor by name or ID.

        :param name_or_id: Name or ID of the flavor.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"
        :param get_extra:
             Whether or not the list_flavors call should get the extra flavor
             specs.

        :returns: A flavor ``munch.Munch`` or None if no matching flavor is
            found.

        """
        if not filters:
            filters = {}
        flavor = self.compute.find_flavor(
            name_or_id, get_extra_specs=get_extra, **filters)
        if flavor:
            return flavor._to_munch(original_names=False)

    def get_flavor_by_id(self, id, get_extra=False):
        """ Get a flavor by ID

        :param id: ID of the flavor.
        :param get_extra:
             Whether or not the list_flavors call should get the extra flavor
             specs.
        :returns: A flavor ``munch.Munch``.
        """
        flavor = self.compute.get_flavor(id, get_extra_specs=get_extra)
        return flavor._to_munch(original_names=False)

    def get_server_console(self, server, length=None):
        """Get the console log for a server.

        :param server: The server to fetch the console log for. Can be either
                       a server dict or the Name or ID of the server.
        :param int length: The number of lines you would like to retrieve from
                           the end of the log. (optional, defaults to all)

        :returns: A string containing the text of the console log or an
                  empty string if the cloud does not support console logs.
        :raises: OpenStackCloudException if an invalid server argument is given
                 or if something else unforseen happens
        """

        if not isinstance(server, dict):
            server = self.get_server(server, bare=True)

        if not server:
            raise exc.OpenStackCloudException(
                "Console log requested for invalid server")

        try:
            return self._get_server_console_output(server['id'], length)
        except exc.OpenStackCloudBadRequest:
            return ""

    def _get_server_console_output(self, server_id, length=None):
        output = self.compute.get_server_console_output(
            server=server_id,
            length=length
        )
        if 'output' in output:
            return output['output']

    def get_server(
            self, name_or_id=None, filters=None, detailed=False, bare=False,
            all_projects=False):
        """Get a server by name or ID.

        :param name_or_id: Name or ID of the server.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'last_name': 'Smith',
                  'other': {
                      'gender': 'Female'
                  }
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"
        :param detailed: Whether or not to add detailed additional information.
                         Defaults to False.
        :param bare: Whether to skip adding any additional information to the
                     server record. Defaults to False, meaning the addresses
                     dict will be populated as needed from neutron. Setting
                     to True implies detailed = False.
        :param all_projects: Whether to get server from all projects or just
                             the current auth scoped project.

        :returns: A server ``munch.Munch`` or None if no matching server is
                  found.

        """
        searchfunc = functools.partial(self.search_servers,
                                       detailed=detailed, bare=True,
                                       all_projects=all_projects)
        server = _utils._get_entity(self, searchfunc, name_or_id, filters)
        return self._expand_server(server, detailed, bare)

    def _expand_server(self, server, detailed, bare):
        if bare or not server:
            return server
        elif detailed:
            return meta.get_hostvars_from_server(self, server)
        else:
            return meta.add_server_interfaces(self, server)

    def get_server_by_id(self, id):
        """Get a server by ID.

        :param id: ID of the server.

        :returns: A server dict or None if no matching server is found.
        """
        try:
            data = proxy._json_response(
                self.compute.get('/servers/{id}'.format(id=id)))
            server = self._get_and_munchify('server', data)
            return meta.add_server_interfaces(
                self, self._normalize_server(server))
        except exceptions.ResourceNotFound:
            return None

    def get_server_group(self, name_or_id=None, filters=None):
        """Get a server group by name or ID.

        :param name_or_id: Name or ID of the server group.
        :param filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'policy': 'affinity',
                }

            OR
            A string containing a jmespath expression for further filtering.
            Example:: "[?last_name==`Smith`] | [?other.gender]==`Female`]"

        :returns: A server groups dict or None if no matching server group
                  is found.

        """
        return _utils._get_entity(self, 'server_group', name_or_id,
                                  filters)

    def create_keypair(self, name, public_key=None):
        """Create a new keypair.

        :param name: Name of the keypair being created.
        :param public_key: Public key for the new keypair.

        :raises: OpenStackCloudException on operation error.
        """
        keypair = {
            'name': name,
        }
        if public_key:
            keypair['public_key'] = public_key
        return self.compute.create_keypair(**keypair)

    def delete_keypair(self, name):
        """Delete a keypair.

        :param name: Name of the keypair to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        try:
            self.compute.delete_keypair(name, ignore_missing=False)
        except exceptions.ResourceNotFound:
            self.log.debug("Keypair %s not found for deleting", name)
            return False
        return True

    def create_image_snapshot(
            self, name, server, wait=False, timeout=3600, **metadata):
        """Create an image by snapshotting an existing server.

        ..note::
            On most clouds this is a cold snapshot - meaning that the server
            in question will be shutdown before taking the snapshot. It is
            possible that it's a live snapshot - but there is no way to know
            as a user, so caveat emptor.

        :param name: Name of the image to be created
        :param server: Server name or ID or dict representing the server
                       to be snapshotted
        :param wait: If true, waits for image to be created.
        :param timeout: Seconds to wait for image creation. None is forever.
        :param metadata: Metadata to give newly-created image entity

        :returns: A ``munch.Munch`` of the Image object

        :raises: OpenStackCloudException if there are problems uploading
        """
        if not isinstance(server, dict):
            server_obj = self.get_server(server, bare=True)
            if not server_obj:
                raise exc.OpenStackCloudException(
                    "Server {server} could not be found and therefore"
                    " could not be snapshotted.".format(server=server))
            server = server_obj
        image = self.compute.create_server_image(
            server, name=name, metadata=metadata, wait=wait, timeout=timeout)
        return image

    def get_server_id(self, name_or_id):
        server = self.get_server(name_or_id, bare=True)
        if server:
            return server['id']
        return None

    def get_server_private_ip(self, server):
        return meta.get_server_private_ip(server, self)

    def get_server_public_ip(self, server):
        return meta.get_server_external_ipv4(self, server)

    def get_server_meta(self, server):
        # TODO(mordred) remove once ansible has moved to Inventory interface
        server_vars = meta.get_hostvars_from_server(self, server)
        groups = meta.get_groups_from_server(self, server, server_vars)
        return dict(server_vars=server_vars, groups=groups)

    @_utils.valid_kwargs(
        'meta', 'files', 'userdata',
        'reservation_id', 'return_raw', 'min_count',
        'max_count', 'security_groups', 'key_name',
        'availability_zone', 'block_device_mapping',
        'block_device_mapping_v2', 'nics', 'scheduler_hints',
        'config_drive', 'admin_pass', 'disk_config')
    def create_server(
            self, name, image=None, flavor=None,
            auto_ip=True, ips=None, ip_pool=None,
            root_volume=None, terminate_volume=False,
            wait=False, timeout=180, reuse_ips=True,
            network=None, boot_from_volume=False, volume_size='50',
            boot_volume=None, volumes=None, nat_destination=None,
            group=None,
            **kwargs):
        """Create a virtual server instance.

        :param name: Something to name the server.
        :param image: Image dict, name or ID to boot with. image is required
                      unless boot_volume is given.
        :param flavor: Flavor dict, name or ID to boot onto.
        :param auto_ip: Whether to take actions to find a routable IP for
                        the server. (defaults to True)
        :param ips: List of IPs to attach to the server (defaults to None)
        :param ip_pool: Name of the network or floating IP pool to get an
                        address from. (defaults to None)
        :param root_volume: Name or ID of a volume to boot from
                            (defaults to None - deprecated, use boot_volume)
        :param boot_volume: Name or ID of a volume to boot from
                            (defaults to None)
        :param terminate_volume: If booting from a volume, whether it should
                                 be deleted when the server is destroyed.
                                 (defaults to False)
        :param volumes: (optional) A list of volumes to attach to the server
        :param meta: (optional) A dict of arbitrary key/value metadata to
                     store for this server. Both keys and values must be
                     <=255 characters.
        :param files: (optional, deprecated) A dict of files to overwrite
                      on the server upon boot. Keys are file names (i.e.
                      ``/etc/passwd``) and values
                      are the file contents (either as a string or as a
                      file-like object). A maximum of five entries is allowed,
                      and each file must be 10k or less.
        :param reservation_id: a UUID for the set of servers being requested.
        :param min_count: (optional extension) The minimum number of
                          servers to launch.
        :param max_count: (optional extension) The maximum number of
                          servers to launch.
        :param security_groups: A list of security group names
        :param userdata: user data to pass to be exposed by the metadata
                      server this can be a file type object as well or a
                      string.
        :param key_name: (optional extension) name of previously created
                      keypair to inject into the instance.
        :param availability_zone: Name of the availability zone for instance
                                  placement.
        :param block_device_mapping: (optional) A dict of block
                      device mappings for this server.
        :param block_device_mapping_v2: (optional) A dict of block
                      device mappings for this server.
        :param nics:  (optional extension) an ordered list of nics to be
                      added to this server, with information about
                      connected networks, fixed IPs, port etc.
        :param scheduler_hints: (optional extension) arbitrary key-value pairs
                            specified by the client to help boot an instance
        :param config_drive: (optional extension) value for config drive
                            either boolean, or volume-id
        :param disk_config: (optional extension) control how the disk is
                            partitioned when the server is created.  possible
                            values are 'AUTO' or 'MANUAL'.
        :param admin_pass: (optional extension) add a user supplied admin
                           password.
        :param wait: (optional) Wait for the address to appear as assigned
                     to the server. Defaults to False.
        :param timeout: (optional) Seconds to wait, defaults to 60.
                        See the ``wait`` parameter.
        :param reuse_ips: (optional) Whether to attempt to reuse pre-existing
                                     floating ips should a floating IP be
                                     needed (defaults to True)
        :param network: (optional) Network dict or name or ID to attach the
                        server to.  Mutually exclusive with the nics parameter.
                        Can also be a list of network names or IDs or
                        network dicts.
        :param boot_from_volume: Whether to boot from volume. 'boot_volume'
                                 implies True, but boot_from_volume=True with
                                 no boot_volume is valid and will create a
                                 volume from the image and use that.
        :param volume_size: When booting an image from volume, how big should
                            the created volume be? Defaults to 50.
        :param nat_destination: Which network should a created floating IP
                                be attached to, if it's not possible to
                                infer from the cloud's configuration.
                                (Optional, defaults to None)
        :param group: ServerGroup dict, name or id to boot the server in.
                      If a group is provided in both scheduler_hints and in
                      the group param, the group param will win.
                      (Optional, defaults to None)
        :returns: A ``munch.Munch`` representing the created server.
        :raises: OpenStackCloudException on operation error.
        """
        # TODO(shade) Image is optional but flavor is not - yet flavor comes
        # after image in the argument list. Doh.
        if not flavor:
            raise TypeError(
                "create_server() missing 1 required argument: 'flavor'")
        if not image and not boot_volume:
            raise TypeError(
                "create_server() requires either 'image' or 'boot_volume'")

        microversion = None
        server_json = {'server': kwargs}

        # TODO(mordred) Add support for description starting in 2.19
        security_groups = kwargs.get('security_groups', [])
        if security_groups and not isinstance(kwargs['security_groups'], list):
            security_groups = [security_groups]
        if security_groups:
            kwargs['security_groups'] = []
            for sec_group in security_groups:
                kwargs['security_groups'].append(dict(name=sec_group))
        if 'userdata' in kwargs:
            user_data = kwargs.pop('userdata')
            if user_data:
                kwargs['user_data'] = self._encode_server_userdata(user_data)
        for (desired, given) in (
                ('OS-DCF:diskConfig', 'disk_config'),
                ('config_drive', 'config_drive'),
                ('key_name', 'key_name'),
                ('metadata', 'meta'),
                ('adminPass', 'admin_pass')):
            value = kwargs.pop(given, None)
            if value:
                kwargs[desired] = value

        hints = kwargs.pop('scheduler_hints', {})
        if group:
            group_obj = self.get_server_group(group)
            if not group_obj:
                raise exc.OpenStackCloudException(
                    "Server Group {group} was requested but was not found"
                    " on the cloud".format(group=group))
            hints['group'] = group_obj['id']
        if hints:
            server_json['os:scheduler_hints'] = hints
        kwargs.setdefault('max_count', kwargs.get('max_count', 1))
        kwargs.setdefault('min_count', kwargs.get('min_count', 1))

        if 'nics' in kwargs and not isinstance(kwargs['nics'], list):
            if isinstance(kwargs['nics'], dict):
                # Be nice and help the user out
                kwargs['nics'] = [kwargs['nics']]
            else:
                raise exc.OpenStackCloudException(
                    'nics parameter to create_server takes a list of dicts.'
                    ' Got: {nics}'.format(nics=kwargs['nics']))

        if network and ('nics' not in kwargs or not kwargs['nics']):
            nics = []
            if not isinstance(network, list):
                network = [network]
            for net_name in network:
                if isinstance(net_name, dict) and 'id' in net_name:
                    network_obj = net_name
                else:
                    network_obj = self.get_network(name_or_id=net_name)
                if not network_obj:
                    raise exc.OpenStackCloudException(
                        'Network {network} is not a valid network in'
                        ' {cloud}:{region}'.format(
                            network=network,
                            cloud=self.name, region=self._compute_region))
                nics.append({'net-id': network_obj['id']})

            kwargs['nics'] = nics
        if not network and ('nics' not in kwargs or not kwargs['nics']):
            default_network = self.get_default_network()
            if default_network:
                kwargs['nics'] = [{'net-id': default_network['id']}]

        networks = []
        for nic in kwargs.pop('nics', []):
            net = {}
            if 'net-id' in nic:
                # TODO(mordred) Make sure this is in uuid format
                net['uuid'] = nic.pop('net-id')
                # If there's a net-id, ignore net-name
                nic.pop('net-name', None)
            elif 'net-name' in nic:
                net_name = nic.pop('net-name')
                nic_net = self.get_network(net_name)
                if not nic_net:
                    raise exc.OpenStackCloudException(
                        "Requested network {net} could not be found.".format(
                            net=net_name))
                net['uuid'] = nic_net['id']
            for ip_key in ('v4-fixed-ip', 'v6-fixed-ip', 'fixed_ip'):
                fixed_ip = nic.pop(ip_key, None)
                if fixed_ip and net.get('fixed_ip'):
                    raise exc.OpenStackCloudException(
                        "Only one of v4-fixed-ip, v6-fixed-ip or fixed_ip"
                        " may be given")
                if fixed_ip:
                    net['fixed_ip'] = fixed_ip
            for key in ('port', 'port-id'):
                if key in nic:
                    net['port'] = nic.pop(key)
            # A tag supported only in server microversion 2.32-2.36 or >= 2.42
            # Bumping the version to 2.42 to support the 'tag' implementation
            if 'tag' in nic:
                microversion = utils.pick_microversion(self.compute, '2.42')
                net['tag'] = nic.pop('tag')
            if nic:
                raise exc.OpenStackCloudException(
                    "Additional unsupported keys given for server network"
                    " creation: {keys}".format(keys=nic.keys()))
            networks.append(net)
        if networks:
            kwargs['networks'] = networks

        if image:
            if isinstance(image, dict):
                kwargs['imageRef'] = image['id']
            else:
                kwargs['imageRef'] = self.get_image(image).id
        if isinstance(flavor, dict):
            kwargs['flavorRef'] = flavor['id']
        else:
            kwargs['flavorRef'] = self.get_flavor(flavor, get_extra=False).id

        if volumes is None:
            volumes = []

        # nova cli calls this boot_volume. Let's be the same
        if root_volume and not boot_volume:
            boot_volume = root_volume

        kwargs = self._get_boot_from_volume_kwargs(
            image=image, boot_from_volume=boot_from_volume,
            boot_volume=boot_volume, volume_size=str(volume_size),
            terminate_volume=terminate_volume,
            volumes=volumes, kwargs=kwargs)

        kwargs['name'] = name
        endpoint = '/servers'
        # TODO(mordred) We're only testing this in functional tests. We need
        # to add unit tests for this too.
        if 'block_device_mapping_v2' in kwargs:
            endpoint = '/os-volumes_boot'
        with _utils.shade_exceptions("Error in creating instance"):
            data = proxy._json_response(
                self.compute.post(endpoint, json=server_json,
                                  microversion=microversion))
            server = self._get_and_munchify('server', data)
            admin_pass = server.get('adminPass') or kwargs.get('admin_pass')
            if not wait:
                # This is a direct get call to skip the list_servers
                # cache which has absolutely no chance of containing the
                # new server.
                # Only do this if we're not going to wait for the server
                # to complete booting, because the only reason we do it
                # is to get a server record that is the return value from
                # get/list rather than the return value of create. If we're
                # going to do the wait loop below, this is a waste of a call
                server = self.get_server_by_id(server.id)
                if server.status == 'ERROR':
                    raise exc.OpenStackCloudCreateException(
                        resource='server', resource_id=server.id)

        if wait:
            server = self.wait_for_server(
                server,
                auto_ip=auto_ip, ips=ips, ip_pool=ip_pool,
                reuse=reuse_ips, timeout=timeout,
                nat_destination=nat_destination,
            )

        server.adminPass = admin_pass
        return server

    def _get_boot_from_volume_kwargs(
            self, image, boot_from_volume, boot_volume, volume_size,
            terminate_volume, volumes, kwargs):
        """Return block device mappings

        :param image: Image dict, name or id to boot with.

        """
        # TODO(mordred) We're only testing this in functional tests. We need
        # to add unit tests for this too.
        if boot_volume or boot_from_volume or volumes:
            kwargs.setdefault('block_device_mapping_v2', [])
        else:
            return kwargs

        # If we have boot_from_volume but no root volume, then we're
        # booting an image from volume
        if boot_volume:
            volume = self.get_volume(boot_volume)
            if not volume:
                raise exc.OpenStackCloudException(
                    'Volume {boot_volume} is not a valid volume'
                    ' in {cloud}:{region}'.format(
                        boot_volume=boot_volume,
                        cloud=self.name, region=self._compute_region))
            block_mapping = {
                'boot_index': '0',
                'delete_on_termination': terminate_volume,
                'destination_type': 'volume',
                'uuid': volume['id'],
                'source_type': 'volume',
            }
            kwargs['block_device_mapping_v2'].append(block_mapping)
            kwargs['imageRef'] = ''
        elif boot_from_volume:

            if isinstance(image, dict):
                image_obj = image
            else:
                image_obj = self.get_image(image)
            if not image_obj:
                raise exc.OpenStackCloudException(
                    'Image {image} is not a valid image in'
                    ' {cloud}:{region}'.format(
                        image=image,
                        cloud=self.name, region=self._compute_region))

            block_mapping = {
                'boot_index': '0',
                'delete_on_termination': terminate_volume,
                'destination_type': 'volume',
                'uuid': image_obj['id'],
                'source_type': 'image',
                'volume_size': volume_size,
            }
            kwargs['imageRef'] = ''
            kwargs['block_device_mapping_v2'].append(block_mapping)
        if volumes and kwargs['imageRef']:
            # If we're attaching volumes on boot but booting from an image,
            # we need to specify that in the BDM.
            block_mapping = {
                u'boot_index': 0,
                u'delete_on_termination': True,
                u'destination_type': u'local',
                u'source_type': u'image',
                u'uuid': kwargs['imageRef'],
            }
            kwargs['block_device_mapping_v2'].append(block_mapping)
        for volume in volumes:
            volume_obj = self.get_volume(volume)
            if not volume_obj:
                raise exc.OpenStackCloudException(
                    'Volume {volume} is not a valid volume'
                    ' in {cloud}:{region}'.format(
                        volume=volume,
                        cloud=self.name, region=self._compute_region))
            block_mapping = {
                'boot_index': '-1',
                'delete_on_termination': False,
                'destination_type': 'volume',
                'uuid': volume_obj['id'],
                'source_type': 'volume',
            }
            kwargs['block_device_mapping_v2'].append(block_mapping)
        if boot_volume or boot_from_volume or volumes:
            self.list_volumes.invalidate(self)
        return kwargs

    def wait_for_server(
            self, server, auto_ip=True, ips=None, ip_pool=None,
            reuse=True, timeout=180, nat_destination=None):
        """
        Wait for a server to reach ACTIVE status.
        """
        # server = self.compute.wait_for_server(
        #     server=server, interval=self._SERVER_AGE or 2, wait=timeout
        # )
        server_id = server['id']
        timeout_message = "Timeout waiting for the server to come up."
        start_time = time.time()

        # There is no point in iterating faster than the list_servers cache
        for count in utils.iterate_timeout(
                timeout,
                timeout_message,
                # if _SERVER_AGE is 0 we still want to wait a bit
                # to be friendly with the server.
                wait=self._SERVER_AGE or 2):
            try:
                # Use the get_server call so that the list_servers
                # cache can be leveraged
                server = self.get_server(server_id)
            except Exception:
                continue
            if not server:
                continue

            # We have more work to do, but the details of that are
            # hidden from the user. So, calculate remaining timeout
            # and pass it down into the IP stack.
            remaining_timeout = timeout - int(time.time() - start_time)
            if remaining_timeout <= 0:
                raise exc.OpenStackCloudTimeout(timeout_message)

            server = self.get_active_server(
                server=server, reuse=reuse,
                auto_ip=auto_ip, ips=ips, ip_pool=ip_pool,
                wait=True, timeout=remaining_timeout,
                nat_destination=nat_destination)

            if server is not None and server['status'] == 'ACTIVE':
                return server

    def get_active_server(
            self, server, auto_ip=True, ips=None, ip_pool=None,
            reuse=True, wait=False, timeout=180, nat_destination=None):

        if server['status'] == 'ERROR':
            if 'fault' in server and 'message' in server['fault']:
                raise exc.OpenStackCloudException(
                    "Error in creating the server."
                    " Compute service reports fault: {reason}".format(
                        reason=server['fault']['message']),
                    extra_data=dict(server=server))

            raise exc.OpenStackCloudException(
                "Error in creating the server"
                " (no further information available)",
                extra_data=dict(server=server))

        if server['status'] == 'ACTIVE':
            if 'addresses' in server and server['addresses']:
                return self.add_ips_to_server(
                    server, auto_ip, ips, ip_pool, reuse=reuse,
                    nat_destination=nat_destination,
                    wait=wait, timeout=timeout)

            self.log.debug(
                'Server %(server)s reached ACTIVE state without'
                ' being allocated an IP address.'
                ' Deleting server.', {'server': server['id']})
            try:
                self._delete_server(
                    server=server, wait=wait, timeout=timeout)
            except Exception as e:
                raise exc.OpenStackCloudException(
                    'Server reached ACTIVE state without being'
                    ' allocated an IP address AND then could not'
                    ' be deleted: {0}'.format(e),
                    extra_data=dict(server=server))
            raise exc.OpenStackCloudException(
                'Server reached ACTIVE state without being'
                ' allocated an IP address.',
                extra_data=dict(server=server))
        return None

    def rebuild_server(self, server_id, image_id, admin_pass=None,
                       detailed=False, bare=False,
                       wait=False, timeout=180):
        kwargs = {}
        if image_id:
            kwargs['imageRef'] = image_id
        if admin_pass:
            kwargs['adminPass'] = admin_pass

        data = proxy._json_response(
            self.compute.post(
                '/servers/{server_id}/action'.format(server_id=server_id),
                json={'rebuild': kwargs}),
            error_message="Error in rebuilding instance")
        server = self._get_and_munchify('server', data)
        if not wait:
            return self._expand_server(
                self._normalize_server(server), bare=bare, detailed=detailed)

        admin_pass = server.get('adminPass') or admin_pass
        for count in utils.iterate_timeout(
                timeout,
                "Timeout waiting for server {0} to "
                "rebuild.".format(server_id),
                wait=self._SERVER_AGE):
            try:
                server = self.get_server(server_id, bare=True)
            except Exception:
                continue
            if not server:
                continue

            if server['status'] == 'ERROR':
                raise exc.OpenStackCloudException(
                    "Error in rebuilding the server",
                    extra_data=dict(server=server))

            if server['status'] == 'ACTIVE':
                server.adminPass = admin_pass
                break

        return self._expand_server(server, detailed=detailed, bare=bare)

    def set_server_metadata(self, name_or_id, metadata):
        """Set metadata in a server instance.

        :param str name_or_id: The name or ID of the server instance
            to update.
        :param dict metadata: A dictionary with the key=value pairs
            to set in the server instance. It only updates the key=value
            pairs provided. Existing ones will remain untouched.

        :raises: OpenStackCloudException on operation error.
        """
        server = self.get_server(name_or_id, bare=True)
        if not server:
            raise exc.OpenStackCloudException(
                'Invalid Server {server}'.format(server=name_or_id))

        self.compute.set_server_metadata(server=server.id, **metadata)

    def delete_server_metadata(self, name_or_id, metadata_keys):
        """Delete metadata from a server instance.

        :param str name_or_id: The name or ID of the server instance
            to update.
        :param metadata_keys: A list with the keys to be deleted
            from the server instance.

        :raises: OpenStackCloudException on operation error.
        """
        server = self.get_server(name_or_id, bare=True)
        if not server:
            raise exc.OpenStackCloudException(
                'Invalid Server {server}'.format(server=name_or_id))

        self.compute.delete_server_metadata(server=server.id,
                                            keys=metadata_keys)

    def delete_server(
            self, name_or_id, wait=False, timeout=180, delete_ips=False,
            delete_ip_retry=1):
        """Delete a server instance.

        :param name_or_id: name or ID of the server to delete
        :param bool wait: If true, waits for server to be deleted.
        :param int timeout: Seconds to wait for server deletion.
        :param bool delete_ips: If true, deletes any floating IPs
            associated with the instance.
        :param int delete_ip_retry: Number of times to retry deleting
            any floating ips, should the first try be unsuccessful.

        :returns: True if delete succeeded, False otherwise if the
            server does not exist.

        :raises: OpenStackCloudException on operation error.
        """
        # If delete_ips is True, we need the server to not be bare.
        server = self.get_server(name_or_id, bare=True)
        if not server:
            return False

        # This portion of the code is intentionally left as a separate
        # private method in order to avoid an unnecessary API call to get
        # a server we already have.
        return self._delete_server(
            server, wait=wait, timeout=timeout, delete_ips=delete_ips,
            delete_ip_retry=delete_ip_retry)

    def _delete_server_floating_ips(self, server, delete_ip_retry):
        # Does the server have floating ips in its
        # addresses dict? If not, skip this.
        server_floats = meta.find_nova_interfaces(
            server['addresses'], ext_tag='floating')
        for fip in server_floats:
            try:
                ip = self.get_floating_ip(id=None, filters={
                    'floating_ip_address': fip['addr']})
            except exc.OpenStackCloudURINotFound:
                # We're deleting. If it doesn't exist - awesome
                # NOTE(mordred) If the cloud is a nova FIP cloud but
                #               floating_ip_source is set to neutron, this
                #               can lead to a FIP leak.
                continue
            if not ip:
                continue
            deleted = self.delete_floating_ip(
                ip['id'], retry=delete_ip_retry)
            if not deleted:
                raise exc.OpenStackCloudException(
                    "Tried to delete floating ip {floating_ip}"
                    " associated with server {id} but there was"
                    " an error deleting it. Not deleting server.".format(
                        floating_ip=ip['floating_ip_address'],
                        id=server['id']))

    def _delete_server(
            self, server, wait=False, timeout=180, delete_ips=False,
            delete_ip_retry=1):
        if not server:
            return False

        if delete_ips and self._has_floating_ips():
            self._delete_server_floating_ips(server, delete_ip_retry)

        try:
            proxy._json_response(
                self.compute.delete(
                    '/servers/{id}'.format(id=server['id'])),
                error_message="Error in deleting server")
        except exc.OpenStackCloudURINotFound:
            return False
        except Exception:
            raise

        if not wait:
            return True

        # If the server has volume attachments, or if it has booted
        # from volume, deleting it will change volume state so we will
        # need to invalidate the cache. Avoid the extra API call if
        # caching is not enabled.
        reset_volume_cache = False
        if (self.cache_enabled
                and self.has_service('volume')
                and self.get_volumes(server)):
            reset_volume_cache = True

        for count in utils.iterate_timeout(
                timeout,
                "Timed out waiting for server to get deleted.",
                # if _SERVER_AGE is 0 we still want to wait a bit
                # to be friendly with the server.
                wait=self._SERVER_AGE or 2):
            with _utils.shade_exceptions("Error in deleting server"):
                server = self.get_server(server['id'], bare=True)
                if not server:
                    break

        if reset_volume_cache:
            self.list_volumes.invalidate(self)

        # Reset the list servers cache time so that the next list server
        # call gets a new list
        self._servers_time = self._servers_time - self._SERVER_AGE
        return True

    @_utils.valid_kwargs(
        'name', 'description')
    def update_server(self, name_or_id, detailed=False, bare=False, **kwargs):
        """Update a server.

        :param name_or_id: Name of the server to be updated.
        :param detailed: Whether or not to add detailed additional information.
                         Defaults to False.
        :param bare: Whether to skip adding any additional information to the
                     server record. Defaults to False, meaning the addresses
                     dict will be populated as needed from neutron. Setting
                     to True implies detailed = False.
        :name: New name for the server
        :description: New description for the server

        :returns: a dictionary representing the updated server.

        :raises: OpenStackCloudException on operation error.
        """
        server = self.get_server(name_or_id=name_or_id, bare=True)
        if server is None:
            raise exc.OpenStackCloudException(
                "failed to find server '{server}'".format(server=name_or_id))

        data = proxy._json_response(
            self.compute.put(
                '/servers/{server_id}'.format(server_id=server['id']),
                json={'server': kwargs}),
            error_message="Error updating server {0}".format(name_or_id))
        server = self._normalize_server(
            self._get_and_munchify('server', data))
        return self._expand_server(server, bare=bare, detailed=detailed)

    def create_server_group(self, name, policies=[], policy=None):
        """Create a new server group.

        :param name: Name of the server group being created
        :param policies: List of policies for the server group.

        :returns: a dict representing the new server group.

        :raises: OpenStackCloudException on operation error.
        """
        sg_attrs = {
            'name': name
        }
        if policies:
            sg_attrs['policies'] = policies
        if policy:
            sg_attrs['policy'] = policy
        return self.compute.create_server_group(
            **sg_attrs
        )

    def delete_server_group(self, name_or_id):
        """Delete a server group.

        :param name_or_id: Name or ID of the server group to delete

        :returns: True if delete succeeded, False otherwise

        :raises: OpenStackCloudException on operation error.
        """
        server_group = self.get_server_group(name_or_id)
        if not server_group:
            self.log.debug("Server group %s not found for deleting",
                           name_or_id)
            return False

        self.compute.delete_server_group(server_group, ignore_missing=False)
        return True

    def create_flavor(self, name, ram, vcpus, disk, flavorid="auto",
                      ephemeral=0, swap=0, rxtx_factor=1.0, is_public=True):
        """Create a new flavor.

        :param name: Descriptive name of the flavor
        :param ram: Memory in MB for the flavor
        :param vcpus: Number of VCPUs for the flavor
        :param disk: Size of local disk in GB
        :param flavorid: ID for the flavor (optional)
        :param ephemeral: Ephemeral space size in GB
        :param swap: Swap space in MB
        :param rxtx_factor: RX/TX factor
        :param is_public: Make flavor accessible to the public

        :returns: A ``munch.Munch`` describing the new flavor.

        :raises: OpenStackCloudException on operation error.
        """
        attrs = {
            'disk': disk,
            'ephemeral': ephemeral,
            'id': flavorid,
            'is_public': is_public,
            'name': name,
            'ram': ram,
            'rxtx_factor': rxtx_factor,
            'swap': swap,
            'vcpus': vcpus,
        }
        if flavorid == 'auto':
            attrs['id'] = None

        flavor = self.compute.create_flavor(**attrs)

        return flavor._to_munch(original_names=False)

    def delete_flavor(self, name_or_id):
        """Delete a flavor

        :param name_or_id: ID or name of the flavor to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        try:
            flavor = self.compute.find_flavor(name_or_id)
            if not flavor:
                self.log.debug(
                    "Flavor %s not found for deleting", name_or_id)
                return False
            self.compute.delete_flavor(flavor)
            return True
        except exceptions.SDKException:
            raise exceptions.OpenStackCloudException(
                "Unable to delete flavor {name}".format(name=name_or_id))

    def set_flavor_specs(self, flavor_id, extra_specs):
        """Add extra specs to a flavor

        :param string flavor_id: ID of the flavor to update.
        :param dict extra_specs: Dictionary of key-value pairs.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudResourceNotFound if flavor ID is not found.
        """
        self.compute.create_flavor_extra_specs(flavor_id, extra_specs)

    def unset_flavor_specs(self, flavor_id, keys):
        """Delete extra specs from a flavor

        :param string flavor_id: ID of the flavor to update.
        :param keys: List of spec keys to delete.

        :raises: OpenStackCloudException on operation error.
        :raises: OpenStackCloudResourceNotFound if flavor ID is not found.
        """
        for key in keys:
            self.compute.delete_flavor_extra_specs_property(flavor_id, key)

    def add_flavor_access(self, flavor_id, project_id):
        """Grant access to a private flavor for a project/tenant.

        :param string flavor_id: ID of the private flavor.
        :param string project_id: ID of the project/tenant.

        :raises: OpenStackCloudException on operation error.
        """
        self.compute.flavor_add_tenant_access(flavor_id, project_id)

    def remove_flavor_access(self, flavor_id, project_id):
        """Revoke access from a private flavor for a project/tenant.

        :param string flavor_id: ID of the private flavor.
        :param string project_id: ID of the project/tenant.

        :raises: OpenStackCloudException on operation error.
        """
        self.compute.flavor_remove_tenant_access(flavor_id, project_id)

    def list_flavor_access(self, flavor_id):
        """List access from a private flavor for a project/tenant.

        :param string flavor_id: ID of the private flavor.

        :returns: a list of ``munch.Munch`` containing the access description

        :raises: OpenStackCloudException on operation error.
        """
        access = self.compute.get_flavor_access(flavor_id)
        return _utils.normalize_flavor_accesses(access)

    def list_hypervisors(self, filters={}):
        """List all hypervisors

        :returns: A list of hypervisor ``munch.Munch``.
        """

        return list(self.compute.hypervisors(
            details=True,
            allow_unknown_params=True,
            **filters))

    def search_aggregates(self, name_or_id=None, filters=None):
        """Seach host aggregates.

        :param name: aggregate name or id.
        :param filters: a dict containing additional filters to use.

        :returns: a list of dicts containing the aggregates

        :raises: ``OpenStackCloudException``: if something goes wrong during
            the OpenStack API call.
        """
        aggregates = self.list_aggregates()
        return _utils._filter_list(aggregates, name_or_id, filters)

    def list_aggregates(self, filters={}):
        """List all available host aggregates.

        :returns: A list of aggregate dicts.

        """
        return self.compute.aggregates(allow_unknown_params=True, **filters)

    def get_aggregate(self, name_or_id, filters=None):
        """Get an aggregate by name or ID.

        :param name_or_id: Name or ID of the aggregate.
        :param dict filters:
            A dictionary of meta data to use for further filtering. Elements
            of this dictionary may, themselves, be dictionaries. Example::

                {
                  'availability_zone': 'nova',
                  'metadata': {
                      'cpu_allocation_ratio': '1.0'
                  }
                }

        :returns: An aggregate dict or None if no matching aggregate is
                  found.

        """
        aggregate = self.compute.find_aggregate(
            name_or_id, ignore_missing=True)
        if aggregate:
            return aggregate._to_munch()

    def create_aggregate(self, name, availability_zone=None):
        """Create a new host aggregate.

        :param name: Name of the host aggregate being created
        :param availability_zone: Availability zone to assign hosts

        :returns: a dict representing the new host aggregate.

        :raises: OpenStackCloudException on operation error.
        """
        return self.compute.create_aggregate(
            name=name,
            availability_zone=availability_zone
        )

    @_utils.valid_kwargs('name', 'availability_zone')
    def update_aggregate(self, name_or_id, **kwargs):
        """Update a host aggregate.

        :param name_or_id: Name or ID of the aggregate being updated.
        :param name: New aggregate name
        :param availability_zone: Availability zone to assign to hosts

        :returns: a dict representing the updated host aggregate.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        return self.compute.update_aggregate(aggregate, **kwargs)

    def delete_aggregate(self, name_or_id):
        """Delete a host aggregate.

        :param name_or_id: Name or ID of the host aggregate to delete.

        :returns: True if delete succeeded, False otherwise.

        :raises: OpenStackCloudException on operation error.
        """
        if (
            isinstance(name_or_id, (str, bytes))
            and not name_or_id.isdigit()
        ):
            aggregate = self.get_aggregate(name_or_id)
            if not aggregate:
                self.log.debug(
                    "Aggregate %s not found for deleting", name_or_id)
                return False
            name_or_id = aggregate.id
        try:
            self.compute.delete_aggregate(name_or_id, ignore_missing=False)
            return True
        except exceptions.ResourceNotFound:
            self.log.debug("Aggregate %s not found for deleting", name_or_id)
            return False

    def set_aggregate_metadata(self, name_or_id, metadata):
        """Set aggregate metadata, replacing the existing metadata.

        :param name_or_id: Name of the host aggregate to update
        :param metadata: Dict containing metadata to replace (Use
                {'key': None} to remove a key)

        :returns: a dict representing the new host aggregate.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            raise exc.OpenStackCloudException(
                "Host aggregate %s not found." % name_or_id)

        return self.compute.set_aggregate_metadata(aggregate, metadata)

    def add_host_to_aggregate(self, name_or_id, host_name):
        """Add a host to an aggregate.

        :param name_or_id: Name or ID of the host aggregate.
        :param host_name: Host to add.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            raise exc.OpenStackCloudException(
                "Host aggregate %s not found." % name_or_id)

        return self.compute.add_host_to_aggregate(aggregate, host_name)

    def remove_host_from_aggregate(self, name_or_id, host_name):
        """Remove a host from an aggregate.

        :param name_or_id: Name or ID of the host aggregate.
        :param host_name: Host to remove.

        :raises: OpenStackCloudException on operation error.
        """
        aggregate = self.get_aggregate(name_or_id)
        if not aggregate:
            raise exc.OpenStackCloudException(
                "Host aggregate %s not found." % name_or_id)

        return self.compute.remove_host_from_aggregate(aggregate, host_name)

    def set_compute_quotas(self, name_or_id, **kwargs):
        """ Set a quota in a project

        :param name_or_id: project name or id
        :param kwargs: key/value pairs of quota name and quota value

        :raises: OpenStackCloudException if the resource to set the
            quota does not exist.
        """

        proj = self.get_project(name_or_id)
        if not proj:
            raise exc.OpenStackCloudException("project does not exist")

        # compute_quotas = {key: val for key, val in kwargs.items()
        #                  if key in quota.COMPUTE_QUOTAS}
        # TODO(ghe): Manage volume and network quotas
        # network_quotas = {key: val for key, val in kwargs.items()
        #                  if key in quota.NETWORK_QUOTAS}
        # volume_quotas = {key: val for key, val in kwargs.items()
        #                 if key in quota.VOLUME_QUOTAS}

        kwargs['force'] = True
        proxy._json_response(
            self.compute.put(
                '/os-quota-sets/{project}'.format(project=proj.id),
                json={'quota_set': kwargs}),
            error_message="No valid quota or resource")

    def get_compute_quotas(self, name_or_id):
        """ Get quota for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise exc.OpenStackCloudException("project does not exist")
        data = proxy._json_response(
            self.compute.get(
                '/os-quota-sets/{project}'.format(project=proj.id)))
        return self._get_and_munchify('quota_set', data)

    def delete_compute_quotas(self, name_or_id):
        """ Delete quota for a project

        :param name_or_id: project name or id
        :raises: OpenStackCloudException if it's not a valid project or the
                 nova client call failed

        :returns: dict with the quotas
        """
        proj = self.get_project(name_or_id)
        if not proj:
            raise exc.OpenStackCloudException("project does not exist")
        return proxy._json_response(
            self.compute.delete(
                '/os-quota-sets/{project}'.format(project=proj.id)))

    def get_compute_usage(self, name_or_id, start=None, end=None):
        """ Get usage for a specific project

        :param name_or_id: project name or id
        :param start: :class:`datetime.datetime` or string. Start date in UTC
                      Defaults to 2010-07-06T12:00:00Z (the date the OpenStack
                      project was started)
        :param end: :class:`datetime.datetime` or string. End date in UTC.
                    Defaults to now
        :raises: OpenStackCloudException if it's not a valid project

        :returns: Munch object with the usage
        """

        def parse_date(date):
            try:
                return iso8601.parse_date(date)
            except iso8601.iso8601.ParseError:
                # Yes. This is an exception mask. However,iso8601 is an
                # implementation detail - and the error message is actually
                # less informative.
                raise exc.OpenStackCloudException(
                    "Date given, {date}, is invalid. Please pass in a date"
                    " string in ISO 8601 format -"
                    " YYYY-MM-DDTHH:MM:SS".format(
                        date=date))

        def parse_datetime_for_nova(date):
            # Must strip tzinfo from the date- it breaks Nova. Also,
            # Nova is expecting this in UTC. If someone passes in an
            # ISO8601 date string or a datetime with timzeone data attached,
            # strip the timezone data but apply offset math first so that
            # the user's well formed perfectly valid date will be used
            # correctly.
            offset = date.utcoffset()
            if offset:
                date = date - datetime.timedelta(hours=offset)
            return date.replace(tzinfo=None)

        if not start:
            start = parse_date('2010-07-06')
        elif not isinstance(start, datetime.datetime):
            start = parse_date(start)
        if not end:
            end = datetime.datetime.utcnow()
        elif not isinstance(start, datetime.datetime):
            end = parse_date(end)

        start = parse_datetime_for_nova(start)
        end = parse_datetime_for_nova(end)

        proj = self.get_project(name_or_id)
        if not proj:
            raise exc.OpenStackCloudException(
                "project does not exist: {name}".format(name=proj.id))

        data = proxy._json_response(
            self.compute.get(
                '/os-simple-tenant-usage/{project}'.format(project=proj.id),
                params=dict(start=start.isoformat(), end=end.isoformat())),
            error_message="Unable to get usage for project: {name}".format(
                name=proj.id))
        return self._normalize_compute_usage(
            self._get_and_munchify('tenant_usage', data))

    def _encode_server_userdata(self, userdata):
        if hasattr(userdata, 'read'):
            userdata = userdata.read()

        if not isinstance(userdata, bytes):
            # If the userdata passed in is bytes, just send it unmodified
            if not isinstance(userdata, str):
                raise TypeError("%s can't be encoded" % type(userdata))
            # If it's not bytes, make it bytes
            userdata = userdata.encode('utf-8', 'strict')

        # Once we have base64 bytes, make them into a utf-8 string for REST
        return base64.b64encode(userdata).decode('utf-8')

    def get_openstack_vars(self, server):
        return meta.get_hostvars_from_server(self, server)

    def _expand_server_vars(self, server):
        # Used by nodepool
        # TODO(mordred) remove after these make it into what we
        # actually want the API to be.
        return meta.expand_server_vars(self, server)
