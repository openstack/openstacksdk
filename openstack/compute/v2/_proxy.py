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

from openstack.compute.v2 import aggregate as _aggregate
from openstack.compute.v2 import availability_zone
from openstack.compute.v2 import extension
from openstack.compute.v2 import flavor as _flavor
from openstack.compute.v2 import hypervisor as _hypervisor
from openstack.compute.v2 import image as _image
from openstack.compute.v2 import keypair as _keypair
from openstack.compute.v2 import limits
from openstack.compute.v2 import server as _server
from openstack.compute.v2 import server_diagnostics as _server_diagnostics
from openstack.compute.v2 import server_group as _server_group
from openstack.compute.v2 import server_interface as _server_interface
from openstack.compute.v2 import server_ip
from openstack.compute.v2 import service as _service
from openstack.compute.v2 import volume_attachment as _volume_attachment
from openstack import proxy
from openstack import resource


class Proxy(proxy.Proxy):

    def find_extension(self, name_or_id, ignore_missing=True):
        """Find a single extension

        :param name_or_id: The name or ID of an extension.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.extension.Extension` or
                  None
        """
        return self._find(extension.Extension, name_or_id,
                          ignore_missing=ignore_missing)

    def extensions(self):
        """Retrieve a generator of extensions

        :returns: A generator of extension instances.
        :rtype: :class:`~openstack.compute.v2.extension.Extension`
        """
        return self._list(extension.Extension)

    def find_flavor(self, name_or_id, ignore_missing=True):
        """Find a single flavor

        :param name_or_id: The name or ID of a flavor.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.flavor.Flavor` or None
        """
        return self._find(_flavor.Flavor, name_or_id,
                          ignore_missing=ignore_missing)

    def create_flavor(self, **attrs):
        """Create a new flavor from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.compute.v2.flavor.Flavor`,
                           comprised of the properties on the Flavor class.

        :returns: The results of flavor creation
        :rtype: :class:`~openstack.compute.v2.flavor.Flavor`
        """
        return self._create(_flavor.Flavor, **attrs)

    def delete_flavor(self, flavor, ignore_missing=True):
        """Delete a flavor

        :param flavor: The value can be either the ID of a flavor or a
                       :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the flavor does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent flavor.

        :returns: ``None``
        """
        self._delete(_flavor.Flavor, flavor, ignore_missing=ignore_missing)

    def get_flavor(self, flavor):
        """Get a single flavor

        :param flavor: The value can be the ID of a flavor or a
                       :class:`~openstack.compute.v2.flavor.Flavor` instance.

        :returns: One :class:`~openstack.compute.v2.flavor.Flavor`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_flavor.Flavor, flavor)

    def flavors(self, details=True, **query):
        """Return a generator of flavors

        :param bool details: When ``True``, returns
            :class:`~openstack.compute.v2.flavor.FlavorDetail` objects,
            otherwise :class:`~openstack.compute.v2.flavor.Flavor`.
            *Default: ``True``*
        :param kwargs query: Optional query parameters to be sent to limit
                                 the flavors being returned.

        :returns: A generator of flavor objects
        """
        flv = _flavor.FlavorDetail if details else _flavor.Flavor
        return self._list(flv, **query)

    def aggregates(self):
        """Return a generator of aggregate

        :returns: A generator of aggregate
        :rtype: class: `~openstack.compute.v2.aggregate.Aggregate`
        """
        aggregate = _aggregate.Aggregate

        return self._list(aggregate)

    def get_aggregate(self, aggregate):
        """Get a single host aggregate

        :param image: The value can be the ID of an aggregate or a
                      :class:`~openstack.compute.v2.aggregate.Aggregate`
                      instance.

        :returns: One :class:`~openstack.compute.v2.aggregate.Aggregate`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_aggregate.Aggregate, aggregate)

    def create_aggregate(self, **attrs):
        """Create a new host aggregate from attributes

        :param dict attrs: Keyword arguments which will be used to create a
                           :class:`~openstack.compute.v2.aggregate.Aggregate`,
                           comprised of the properties on the Aggregate class.

        :returns: The results of aggregate creation
        :rtype: :class:`~openstack.compute.v2.aggregate.Aggregate`
        """
        return self._create(_aggregate.Aggregate, **attrs)

    def update_aggregate(self, aggregate, **attrs):
        """Update a host aggregate

        :param server: Either the ID of a host aggregate or a
                       :class:`~openstack.compute.v2.aggregate.Aggregate`
                       instance.
        :attrs kwargs: The attributes to update on the aggregate represented
                       by ``aggregate``.

        :returns: The updated aggregate
        :rtype: :class:`~openstack.compute.v2.aggregate.Aggregate`
        """
        return self._update(_aggregate.Aggregate, aggregate, **attrs)

    def delete_aggregate(self, aggregate, ignore_missing=True):
        """Delete a host aggregate

        :param keypair: The value can be either the ID of an aggregate or a
                        :class:`~openstack.compute.v2.aggregate.Aggregate`
                        instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the aggregate does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent aggregate.

        :returns: ``None``
        """
        self._delete(_aggregate.Aggregate, aggregate,
                     ignore_missing=ignore_missing)

    def add_host_to_aggregate(self, aggregate, host):
        """Adds a host to an aggregate

        :param aggregate: Either the ID of a aggregate or a
                    :class:`~openstack.compute.v2.aggregate.Aggregate`
                    instance.
        :param str host: The host to add to the aggregate

        :returns: One :class:`~openstack.compute.v2.aggregate.Aggregate`
        """
        aggregate = self._get_resource(_aggregate.Aggregate, aggregate)
        return aggregate.add_host(self, host)

    def remove_host_from_aggregate(self, aggregate, host):
        """Removes a host from an aggregate

        :param aggregate: Either the ID of a aggregate or a
                    :class:`~openstack.compute.v2.aggregate.Aggregate`
                    instance.
        :param str host: The host to remove from the aggregate

        :returns: One :class:`~openstack.compute.v2.aggregate.Aggregate`
        """
        aggregate = self._get_resource(_aggregate.Aggregate, aggregate)
        return aggregate.remove_host(self, host)

    def set_aggregate_metadata(self, aggregate, metadata):
        """Creates or replaces metadata for an aggregate

        :param aggregate: Either the ID of a aggregate or a
                    :class:`~openstack.compute.v2.aggregate.Aggregate`
                    instance.
        :param dict metadata: Metadata key and value pairs. The maximum
                    size for each metadata key and value pair
                    is 255 bytes.

        :returns: One :class:`~openstack.compute.v2.aggregate.Aggregate`
        """
        aggregate = self._get_resource(_aggregate.Aggregate, aggregate)
        return aggregate.set_metadata(self, metadata)

    def delete_image(self, image, ignore_missing=True):
        """Delete an image

        :param image: The value can be either the ID of an image or a
                      :class:`~openstack.compute.v2.image.Image` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the image does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent image.

        :returns: ``None``
        """
        self._delete(_image.Image, image, ignore_missing=ignore_missing)

    def find_image(self, name_or_id, ignore_missing=True):
        """Find a single image

        :param name_or_id: The name or ID of a image.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.image.Image` or None
        """
        return self._find(_image.Image, name_or_id,
                          ignore_missing=ignore_missing)

    def get_image(self, image):
        """Get a single image

        :param image: The value can be the ID of an image or a
                      :class:`~openstack.compute.v2.image.Image` instance.

        :returns: One :class:`~openstack.compute.v2.image.Image`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_image.Image, image)

    def images(self, details=True, **query):
        """Return a generator of images

        :param bool details: When ``True``, returns
            :class:`~openstack.compute.v2.image.ImageDetail` objects,
            otherwise :class:`~openstack.compute.v2.image.Image`.
            *Default: ``True``*
        :param kwargs query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of image objects
        """
        img = _image.ImageDetail if details else _image.Image
        return self._list(img, **query)

    def _get_base_resource(self, res, base):
        # Metadata calls for Image and Server can work for both those
        # resources but also ImageDetail and ServerDetail. If we get
        # either class, use it, otherwise create an instance of the base.
        if isinstance(res, base):
            return res
        else:
            return base(id=res)

    def get_image_metadata(self, image):
        """Return a dictionary of metadata for an image

        :param image: Either the ID of an image or a
                       :class:`~openstack.compute.v2.image.Image` or
                       :class:`~openstack.compute.v2.image.ImageDetail`
                       instance.

        :returns: A :class:`~openstack.compute.v2.image.Image` with only the
                  image's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.compute.v2.image.Image`
        """
        res = self._get_base_resource(image, _image.Image)
        metadata = res.get_metadata(self)
        result = _image.Image.existing(id=res.id, metadata=metadata)
        return result

    def set_image_metadata(self, image, **metadata):
        """Update metadata for an image

        :param image: Either the ID of an image or a
                       :class:`~openstack.compute.v2.image.Image` or
                       :class:`~openstack.compute.v2.image.ImageDetail`
                       instance.
        :param kwargs metadata: Key/value pairs to be updated in the image's
                                metadata. No other metadata is modified
                                by this call. All keys and values are stored
                                as Unicode.

        :returns: A :class:`~openstack.compute.v2.image.Image` with only the
                  image's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.compute.v2.image.Image`
        """
        res = self._get_base_resource(image, _image.Image)
        metadata = res.set_metadata(self, **metadata)
        result = _image.Image.existing(id=res.id, metadata=metadata)
        return result

    def delete_image_metadata(self, image, keys):
        """Delete metadata for an image

        Note: This method will do a HTTP DELETE request for every key in keys.

        :param image: Either the ID of an image or a
                       :class:`~openstack.compute.v2.image.Image` or
                       :class:`~openstack.compute.v2.image.ImageDetail`
                       instance.
        :param keys: The keys to delete.

        :rtype: ``None``
        """
        res = self._get_base_resource(image, _image.Image)
        return res.delete_metadata(self, keys)

    def create_keypair(self, **attrs):
        """Create a new keypair from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.compute.v2.keypair.Keypair`,
                           comprised of the properties on the Keypair class.

        :returns: The results of keypair creation
        :rtype: :class:`~openstack.compute.v2.keypair.Keypair`
        """
        return self._create(_keypair.Keypair, **attrs)

    def delete_keypair(self, keypair, ignore_missing=True):
        """Delete a keypair

        :param keypair: The value can be either the ID of a keypair or a
                        :class:`~openstack.compute.v2.keypair.Keypair`
                        instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the keypair does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent keypair.

        :returns: ``None``
        """
        self._delete(_keypair.Keypair, keypair, ignore_missing=ignore_missing)

    def get_keypair(self, keypair):
        """Get a single keypair

        :param keypair: The value can be the ID of a keypair or a
                        :class:`~openstack.compute.v2.keypair.Keypair`
                        instance.

        :returns: One :class:`~openstack.compute.v2.keypair.Keypair`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_keypair.Keypair, keypair)

    def find_keypair(self, name_or_id, ignore_missing=True):
        """Find a single keypair

        :param name_or_id: The name or ID of a keypair.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.keypair.Keypair` or None
        """
        return self._find(_keypair.Keypair, name_or_id,
                          ignore_missing=ignore_missing)

    def keypairs(self):
        """Return a generator of keypairs

        :returns: A generator of keypair objects
        :rtype: :class:`~openstack.compute.v2.keypair.Keypair`
        """
        return self._list(_keypair.Keypair)

    def get_limits(self):
        """Retrieve limits that are applied to the project's account

        :returns: A Limits object, including both
                  :class:`~openstack.compute.v2.limits.AbsoluteLimits` and
                  :class:`~openstack.compute.v2.limits.RateLimits`
        :rtype: :class:`~openstack.compute.v2.limits.Limits`
        """
        return self._get(limits.Limits)

    def create_server(self, **attrs):
        """Create a new server from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.compute.v2.server.Server`,
                           comprised of the properties on the Server class.

        :returns: The results of server creation
        :rtype: :class:`~openstack.compute.v2.server.Server`
        """
        return self._create(_server.Server, **attrs)

    def delete_server(self, server, ignore_missing=True, force=False):
        """Delete a server

        :param server: The value can be either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the server does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server
        :param bool force: When set to ``True``, the server deletion will be
                           forced immediately.

        :returns: ``None``
        """
        if force:
            server = self._get_resource(_server.Server, server)
            server.force_delete(self)
        else:
            self._delete(_server.Server, server, ignore_missing=ignore_missing)

    def find_server(self, name_or_id, ignore_missing=True):
        """Find a single server

        :param name_or_id: The name or ID of a server.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.server.Server` or None
        """
        return self._find(_server.Server, name_or_id,
                          ignore_missing=ignore_missing)

    def get_server(self, server):
        """Get a single server

        :param server: The value can be the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.

        :returns: One :class:`~openstack.compute.v2.server.Server`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_server.Server, server)

    def servers(self, details=True, all_projects=False, **query):
        """Retrieve a generator of servers

        :param bool details: When set to ``False``
                    :class:`~openstack.compute.v2.server.Server` instances
                    will be returned. The default, ``True``, will cause
                    :class:`~openstack.compute.v2.server.ServerDetail`
                    instances to be returned.
        :param kwargs query: Optional query parameters to be sent to limit
            the servers being returned.  Available parameters include:

            * changes_since: A time/date stamp for when the server last changed
                             status.
            * image: An image resource or ID.
            * flavor: A flavor resource or ID.
            * name: Name of the server as a string.  Can be queried with
                    regular expressions. The regular expression
                    ?name=bob returns both bob and bobb.  If you must match on
                    only bob, you can use a regular expression that
                    matches the syntax of the underlying database server that
                    is implemented for Compute, such as MySQL or PostgreSQL.
            * status: Value of the status of the server so that you can filter
                    on "ACTIVE" for example.
            * host: Name of the host as a string.
            * all_projects: Flag to request servers be returned from all
                            projects, not just the currently scoped one.
            * limit: Requests a specified page size of returned items from the
                     query.  Returns a number of items up to the specified
                     limit value. Use the limit parameter to make an initial
                     limited request and use the ID of the last-seen item from
                     the response as the marker parameter value in a subsequent
                     limited request.
            * marker: Specifies the ID of the last-seen item. Use the limit
                      parameter to make an initial limited request and use the
                      ID of the last-seen item from the response as the marker
                      parameter value in a subsequent limited request.

        :returns: A generator of server instances.
        """
        if all_projects:
            query['all_projects'] = True
        srv = _server.ServerDetail if details else _server.Server
        return self._list(srv, **query)

    def update_server(self, server, **attrs):
        """Update a server

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :attrs kwargs: The attributes to update on the server represented
                       by ``server``.

        :returns: The updated server
        :rtype: :class:`~openstack.compute.v2.server.Server`
        """
        return self._update(_server.Server, server, **attrs)

    def change_server_password(self, server, new_password):
        """Change the administrator password

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param str new_password: The new password to be set.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.change_password(self, new_password)

    def get_server_password(self, server):
        """Get the administrator password

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.

        :returns: encrypted password.
        """
        server = self._get_resource(_server.Server, server)
        return server.get_password(self._session)

    def reset_server_state(self, server, state):
        """Reset the state of server

        :param server: The server can be either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server`.
        :param state: The state of the server to be set, `active` or
                      `error` are valid.

        :returns: None
        """
        res = self._get_base_resource(server, _server.Server)
        res.reset_state(self, state)

    def reboot_server(self, server, reboot_type):
        """Reboot a server

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param str reboot_type: The type of reboot to perform.
                                "HARD" and "SOFT" are the current options.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.reboot(self, reboot_type)

    def rebuild_server(self, server, name, admin_password, **attrs):
        """Rebuild a server

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param str name: The name of the server
        :param str admin_password: The administrator password
        :param bool preserve_ephemeral: Indicates whether the server
            is rebuilt with the preservation of the ephemeral partition.
            *Default: False*
        :param str image: The id of an image to rebuild with. *Default: None*
        :param str access_ipv4: The IPv4 address to rebuild with.
                                *Default: None*
        :param str access_ipv6: The IPv6 address to rebuild with.
                                *Default: None*
        :param dict metadata: A dictionary of metadata to rebuild with.
                               *Default: None*
        :param personality: A list of dictionaries, each including a
                            **path** and **contents** key, to be injected
                            into the rebuilt server at launch.
                            *Default: None*

        :returns: The rebuilt :class:`~openstack.compute.v2.server.Server`
                  instance.
        """
        server = self._get_resource(_server.Server, server)
        return server.rebuild(self, name, admin_password, **attrs)

    def resize_server(self, server, flavor):
        """Resize a server

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param flavor: Either the ID of a flavor or a
                       :class:`~openstack.compute.v2.flavor.Flavor` instance.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        flavor_id = resource.Resource._get_id(flavor)
        server.resize(self, flavor_id)

    def confirm_server_resize(self, server):
        """Confirm a server resize

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.confirm_resize(self)

    def revert_server_resize(self, server):
        """Revert a server resize

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.revert_resize(self)

    def create_server_image(self, server, name, metadata=None):
        """Create an image from a server

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param str name: The name of the image to be created.
        :param dict metadata: A dictionary of metadata to be set on the image.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.create_image(self, name, metadata)

    def add_security_group_to_server(self, server, security_group):
        """Add a security group to a server

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param security_group: Either the ID of a security group or a
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            instance.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        security_group_id = resource.Resource._get_id(security_group)
        server.add_security_group(self, security_group_id)

    def remove_security_group_from_server(self, server, security_group):
        """Remove a security group from a server

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param security_group: Either the ID of a security group or a
            :class:`~openstack.network.v2.security_group.SecurityGroup`
            instance.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        security_group_id = resource.Resource._get_id(security_group)
        server.remove_security_group(self, security_group_id)

    def add_fixed_ip_to_server(self, server, network_id):
        """Adds a fixed IP address to a server instance.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param network_id: The ID of the network from which a fixed IP address
                           is about to be allocated.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.add_fixed_ip(self, network_id)

    def remove_fixed_ip_from_server(self, server, address):
        """Removes a fixed IP address from a server instance.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param address: The fixed IP address to be disassociated from the
                        server.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.remove_fixed_ip(self, address)

    def add_floating_ip_to_server(self, server, address, fixed_address=None):
        """Adds a floating IP address to a server instance.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param address: The floating IP address to be added to the server.
        :param fixed_address: The fixed IP address to be associated with the
                              floating IP address. Used when the server is
                              connected to multiple networks.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.add_floating_ip(self, address,
                               fixed_address=fixed_address)

    def remove_floating_ip_from_server(self, server, address):
        """Removes a floating IP address from a server instance.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param address: The floating IP address to be disassociated from the
                        server.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.remove_floating_ip(self, address)

    def backup_server(self, server, name, backup_type, rotation):
        """Backup a server

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param name: The name of the backup image.
        :param backup_type: The type of the backup, for example, daily.
        :param rotation: The rotation of the back up image, the oldest
                         image will be removed when image count exceed
                         the rotation count.

        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.backup(self, name, backup_type, rotation)

    def pause_server(self, server):
        """Pauses a server and changes its status to ``PAUSED``.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.pause(self)

    def unpause_server(self, server):
        """Unpauses a paused server and changes its status to ``ACTIVE``.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.unpause(self)

    def suspend_server(self, server):
        """Suspends a server and changes its status to ``SUSPENDED``.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.suspend(self)

    def resume_server(self, server):
        """Resumes a suspended server and changes its status to ``ACTIVE``.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.resume(self)

    def lock_server(self, server):
        """Locks a server.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.lock(self)

    def unlock_server(self, server):
        """Unlocks a locked server.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.unlock(self)

    def rescue_server(self, server, admin_pass=None, image_ref=None):
        """Puts a server in rescue mode and changes it status to ``RESCUE``.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param admin_pass: The password for the rescued server. If you omit
                           this parameter, the operation generates a new
                           password.
        :param image_ref: The image reference to use to rescue your server.
                          This can be the image ID or its full URL. If you
                          omit this parameter, the base image reference will
                          be used.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.rescue(self, admin_pass=admin_pass,
                      image_ref=image_ref)

    def unrescue_server(self, server):
        """Unrescues a server and changes its status to ``ACTIVE``.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.unrescue(self)

    def evacuate_server(self, server, host=None, admin_pass=None, force=None):
        """Evacuates a server from a failed host to a new host.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param host: An optional parameter specifying the name or ID of the
                     host to which the server is evacuated.
        :param admin_pass: An optional parameter specifying the administrative
                           password to access the evacuated or rebuilt server.
        :param force: Force an evacuation by not verifying the provided
                      destination host by the scheduler. (New in API version
                      2.29).
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.evacuate(self, host=host, admin_pass=admin_pass,
                        force=force)

    def start_server(self, server):
        """Starts a stopped server and changes its state to ``ACTIVE``.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.start(self)

    def stop_server(self, server):
        """Stops a running server and changes its state to ``SHUTOFF``.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.stop(self)

    def shelve_server(self, server):
        """Shelves a server.

        All associated data and resources are kept but anything still in
        memory is not retained. Policy defaults enable only users with
        administrative role or the owner of the server to perform this
        operation. Cloud provides could change this permission though.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.shelve(self)

    def unshelve_server(self, server):
        """Unselves or restores a shelved server.

        Policy defaults enable only users with administrative role or the
        owner of the server to perform this operation. Cloud provides could
        change this permission though.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.unshelve(self)

    def get_server_console_output(self, server, length=None):
        """Return the console output for a server.

        :param server: Either the ID of a server or a
                    :class:`~openstack.compute.v2.server.Server` instance.
        :param length: Optional number of line to fetch from the end of console
                    log. All lines will be returned if this is not specified.
        :returns: The console output as a dict. Control characters will be
                    escaped to create a valid JSON string.
        """
        server = self._get_resource(_server.Server, server)
        return server.get_console_output(self, length=length)

    def wait_for_server(self, server, status='ACTIVE', failures=None,
                        interval=2, wait=120):
        """Wait for a server to be in a particular status.

        :param res: The resource to wait on to reach the specified status.
                    The resource must have a ``status`` attribute.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param status: Desired status.
        :param failures: Statuses that would be interpreted as failures.
        :type failures: :py:class:`list`
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to the desired status failed to occur in specified seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
                 has transited to one of the failure statuses.
        :raises: :class:`~AttributeError` if the resource does not have a
                ``status`` attribute.
        """
        failures = ['ERROR'] if failures is None else failures
        return resource.wait_for_status(
            self, server, status, failures, interval, wait)

    def create_server_interface(self, server, **attrs):
        """Create a new server interface from attributes

        :param server: The server can be either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance
                       that the interface belongs to.
        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.compute.v2.server_interface.ServerInterface`,
            comprised of the properties on the ServerInterface class.

        :returns: The results of server interface creation
        :rtype: :class:`~openstack.compute.v2.server_interface.ServerInterface`
        """
        server_id = resource.Resource._get_id(server)
        return self._create(_server_interface.ServerInterface,
                            server_id=server_id, **attrs)

    def delete_server_interface(self, server_interface, server=None,
                                ignore_missing=True):
        """Delete a server interface

        :param server_interface:
            The value can be either the ID of a server interface or a
            :class:`~openstack.compute.v2.server_interface.ServerInterface`
            instance.
        :param server: This parameter need to be specified when ServerInterface
                       ID is given as value. It can be either the ID of a
                       server or a :class:`~openstack.compute.v2.server.Server`
                       instance that the interface belongs to.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the server interface does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server interface.

        :returns: ``None``
        """
        server_id = self._get_uri_attribute(server_interface, server,
                                            "server_id")
        server_interface = resource.Resource._get_id(server_interface)

        self._delete(_server_interface.ServerInterface,
                     port_id=server_interface,
                     server_id=server_id,
                     ignore_missing=ignore_missing)

    def get_server_interface(self, server_interface, server=None):
        """Get a single server interface

        :param server_interface:
            The value can be the ID of a server interface or a
            :class:`~openstack.compute.v2.server_interface.ServerInterface`
            instance.
        :param server: This parameter need to be specified when ServerInterface
                       ID is given as value. It can be either the ID of a
                       server or a :class:`~openstack.compute.v2.server.Server`
                       instance that the interface belongs to.

        :returns: One
            :class:`~openstack.compute.v2.server_interface.ServerInterface`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        server_id = self._get_uri_attribute(server_interface, server,
                                            "server_id")
        server_interface = resource.Resource._get_id(server_interface)

        return self._get(_server_interface.ServerInterface,
                         server_id=server_id, port_id=server_interface)

    def server_interfaces(self, server):
        """Return a generator of server interfaces

        :param server: The server can be either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server`.

        :returns: A generator of ServerInterface objects
        :rtype: :class:`~openstack.compute.v2.server_interface.ServerInterface`
        """
        server_id = resource.Resource._get_id(server)
        return self._list(_server_interface.ServerInterface,
                          server_id=server_id)

    def server_ips(self, server, network_label=None):
        """Return a generator of server IPs

        :param server: The server can be either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server`.
        :param network_label: The name of a particular network to list
                              IP addresses from.

        :returns: A generator of ServerIP objects
        :rtype: :class:`~openstack.compute.v2.server_ip.ServerIP`
        """
        server_id = resource.Resource._get_id(server)
        return self._list(server_ip.ServerIP,
                          server_id=server_id, network_label=network_label)

    def availability_zones(self, details=False):
        """Return a generator of availability zones

        :param bool details: Return extra details about the availability
                             zones. This defaults to `False` as it generally
                             requires extra permission.

        :returns: A generator of availability zone
        :rtype: :class:`~openstack.compute.v2.availability_zone.\
                        AvailabilityZone`
        """
        if details:
            az = availability_zone.AvailabilityZoneDetail
        else:
            az = availability_zone.AvailabilityZone

        return self._list(az)

    def get_server_metadata(self, server):
        """Return a dictionary of metadata for a server

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` or
                       :class:`~openstack.compute.v2.server.ServerDetail`
                       instance.

        :returns: A :class:`~openstack.compute.v2.server.Server` with only the
                  server's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.compute.v2.server.Server`
        """
        res = self._get_base_resource(server, _server.Server)
        metadata = res.get_metadata(self)
        result = _server.Server.existing(id=res.id, metadata=metadata)
        return result

    def set_server_metadata(self, server, **metadata):
        """Update metadata for a server

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` or
                       :class:`~openstack.compute.v2.server.ServerDetail`
                       instance.
        :param kwargs metadata: Key/value pairs to be updated in the server's
                                metadata. No other metadata is modified
                                by this call. All keys and values are stored
                                as Unicode.

        :returns: A :class:`~openstack.compute.v2.server.Server` with only the
                  server's metadata. All keys and values are Unicode text.
        :rtype: :class:`~openstack.compute.v2.server.Server`
        """
        res = self._get_base_resource(server, _server.Server)
        metadata = res.set_metadata(self, **metadata)
        result = _server.Server.existing(id=res.id, metadata=metadata)
        return result

    def delete_server_metadata(self, server, keys):
        """Delete metadata for a server

        Note: This method will do a HTTP DELETE request for every key in keys.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` or
                       :class:`~openstack.compute.v2.server.ServerDetail`
                       instance.
        :param keys: The keys to delete

        :rtype: ``None``
        """
        res = self._get_base_resource(server, _server.Server)
        return res.delete_metadata(self, keys)

    def create_server_group(self, **attrs):
        """Create a new server group from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.compute.v2.server_group.ServerGroup`,
            comprised of the properties on the ServerGroup class.

        :returns: The results of server group creation
        :rtype: :class:`~openstack.compute.v2.server_group.ServerGroup`
        """
        return self._create(_server_group.ServerGroup, **attrs)

    def delete_server_group(self, server_group, ignore_missing=True):
        """Delete a server group

        :param server_group: The value can be either the ID of a server group
               or a :class:`~openstack.compute.v2.server_group.ServerGroup`
               instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the server group does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server group.

        :returns: ``None``
        """
        self._delete(_server_group.ServerGroup, server_group,
                     ignore_missing=ignore_missing)

    def find_server_group(self, name_or_id, ignore_missing=True):
        """Find a single server group

        :param name_or_id: The name or ID of a server group.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns:
            One :class:`~openstack.compute.v2.server_group.ServerGroup` object
            or None
        """
        return self._find(_server_group.ServerGroup, name_or_id,
                          ignore_missing=ignore_missing)

    def get_server_group(self, server_group):
        """Get a single server group

        :param server_group: The value can be the ID of a server group or a
               :class:`~openstack.compute.v2.server_group.ServerGroup`
               instance.

        :returns:
            A :class:`~openstack.compute.v2.server_group.ServerGroup` object.
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_server_group.ServerGroup, server_group)

    def server_groups(self, **query):
        """Return a generator of server groups

        :param kwargs query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of ServerGroup objects
        :rtype: :class:`~openstack.compute.v2.server_group.ServerGroup`
        """
        return self._list(_server_group.ServerGroup, **query)

    def hypervisors(self, details=False):
        """Return a generator of hypervisor

        :param bool details: When set to the default, ``False``,
                    :class:`~openstack.compute.v2.hypervisor.Hypervisor`
                    instances will be returned. ``True`` will cause
                    :class:`~openstack.compute.v2.hypervisor.HypervisorDetail`
                    instances to be returned.
        :returns: A generator of hypervisor
        :rtype: class: `~openstack.compute.v2.hypervisor.Hypervisor`
        """
        if details:
            hypervisor = _hypervisor.HypervisorDetail
        else:
            hypervisor = _hypervisor.Hypervisor

        return self._list(hypervisor)

    def find_hypervisor(self, name_or_id, ignore_missing=True):
        """Find a hypervisor from name or id to get the corresponding info

        :param name_or_id: The name or id of a hypervisor

        :returns:
            One: class:`~openstack.compute.v2.hypervisor.Hypervisor` object
            or None
        """

        return self._find(_hypervisor.Hypervisor, name_or_id,
                          ignore_missing=ignore_missing)

    def get_hypervisor(self, hypervisor):
        """Get a single hypervisor

        :param hypervisor: The value can be the ID of a hypervisor or a
               :class:`~openstack.compute.v2.hypervisor.Hypervisor`
               instance.

        :returns:
            A :class:`~openstack.compute.v2.hypervisor.Hypervisor` object.
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        return self._get(_hypervisor.Hypervisor, hypervisor)

    def force_service_down(self, service, host, binary):
        """Force a service down

        :param service: Either the ID of a service or a
                       :class:`~openstack.compute.v2.server.Service` instance.
        :param str host: The host where service runs.
        :param str binary: The name of service.

        :returns: None
        """
        service = self._get_resource(_service.Service, service)
        service.force_down(self, host, binary)

    def disable_service(self, service, host, binary, disabled_reason=None):
        """Disable a service

        :param service: Either the ID of a service or a
                       :class:`~openstack.compute.v2.server.Service` instance.
        :param str host: The host where service runs.
        :param str binary: The name of service.
        :param str disabled_reason: The reason of force down a service.

        :returns: None
        """
        service = self._get_resource(_service.Service, service)
        service.disable(self,
                        host, binary,
                        disabled_reason)

    def enable_service(self, service, host, binary):
        """Enable a service

        :param service: Either the ID of a service or a
                       :class:`~openstack.compute.v2.server.Service` instance.
        :param str host: The host where service runs.
        :param str binary: The name of service.


        :returns: None
        """
        service = self._get_resource(_service.Service, service)
        service.enable(self, host, binary)

    def services(self):
        """Return a generator of service

        :returns: A generator of service
        :rtype: class: `~openstack.compute.v2.service.Service`
        """

        return self._list(_service.Service)

    def create_volume_attachment(self, server, **attrs):
        """Create a new volume attachment from attributes

        :param server: The server can be either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`,
            comprised of the properties on the VolumeAttachment class.

        :returns: The results of volume attachment creation
        :rtype:
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`
        """
        server_id = resource.Resource._get_id(server)
        return self._create(_volume_attachment.VolumeAttachment,
                            server_id=server_id, **attrs)

    def update_volume_attachment(self, volume_attachment, server,
                                 **attrs):
        """update a volume attachment

        :param volume_attachment:
            The value can be either the ID of a volume attachment or a
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`
            instance.
        :param server: This parameter need to be specified when
                       VolumeAttachment ID is given as value. It can be
                       either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server`
                       instance that the attachment belongs to.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the volume attachment does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent volume  attachment.

        :returns: ``None``
        """
        server_id = self._get_uri_attribute(volume_attachment, server,
                                            "server_id")
        volume_attachment = resource.Resource._get_id(volume_attachment)

        return self._update(_volume_attachment.VolumeAttachment,
                            attachment_id=volume_attachment,
                            server_id=server_id)

    def delete_volume_attachment(self, volume_attachment, server,
                                 ignore_missing=True):
        """Delete a volume attachment

        :param volume_attachment:
            The value can be either the ID of a volume attachment or a
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`
            instance.
        :param server: This parameter need to be specified when
                       VolumeAttachment ID is given as value. It can be either
                       the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server`
                       instance that the attachment belongs to.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the volume attachment does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent volume attachment.

        :returns: ``None``
        """
        server_id = self._get_uri_attribute(volume_attachment, server,
                                            "server_id")
        volume_attachment = resource.Resource._get_id(volume_attachment)

        self._delete(_volume_attachment.VolumeAttachment,
                     attachment_id=volume_attachment,
                     server_id=server_id,
                     ignore_missing=ignore_missing)

    def get_volume_attachment(self, volume_attachment, server,
                              ignore_missing=True):
        """Get a single volume attachment

        :param volume_attachment:
            The value can be the ID of a volume attachment or a
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`
            instance.
        :param server: This parameter need to be specified when
                       VolumeAttachment ID is given as value. It can be either
                       the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server`
                       instance that the attachment belongs to.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the volume attachment does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent volume attachment.

        :returns: One
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        server_id = self._get_uri_attribute(volume_attachment, server,
                                            "server_id")
        volume_attachment = resource.Resource._get_id(volume_attachment)

        return self._get(_volume_attachment.VolumeAttachment,
                         server_id=server_id,
                         attachment_id=volume_attachment,
                         ignore_missing=ignore_missing)

    def volume_attachments(self, server):
        """Return a generator of volume attachments

        :param server: The server can be either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server`.

        :returns: A generator of VolumeAttachment objects
        :rtype:
            :class:`~openstack.compute.v2.volume_attachment.VolumeAttachment`
        """
        server_id = resource.Resource._get_id(server)
        return self._list(_volume_attachment.VolumeAttachment,
                          server_id=server_id)

    def migrate_server(self, server):
        """Migrate a server from one host to another

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.migrate(self)

    def live_migrate_server(
            self, server, host=None, force=False, block_migration=None):
        """Live migrate a server from one host to target host

        :param server:
            Either the ID of a server or a
            :class:`~openstack.compute.v2.server.Server` instance.
        :param str host:
            The host to which to migrate the server. If the Nova service is
            too old, the host parameter implies force=True which causes the
            Nova scheduler to be bypassed. On such clouds, a ``ValueError``
            will be thrown if ``host`` is given without ``force``.
        :param bool force:
            Force a live-migration by not verifying the provided destination
            host by the scheduler. This is unsafe and not recommended.
        :param block_migration:
            Perform a block live migration to the destination host by the
            scheduler.  Can be 'auto', True or False. Some clouds are too old
            to support 'auto', in which case a ValueError will be thrown. If
            omitted, the value will be 'auto' on clouds that support it, and
            False on clouds that do not.
        :returns: None
        """
        server = self._get_resource(_server.Server, server)
        server.live_migrate(
            self, host,
            force=force,
            block_migration=block_migration)

    def wait_for_delete(self, res, interval=2, wait=120):
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :type resource: A :class:`~openstack.resource.Resource` object.
        :param interval: Number of seconds to wait before to consecutive
                         checks. Default to 2.
        :param wait: Maximum number of seconds to wait before the change.
                     Default to 120.
        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
                 to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait)

    def get_server_diagnostics(self, server):
        """Get a single server diagnostics

        :param server: This parameter need to be specified when ServerInterface
                       ID is given as value. It can be either the ID of a
                       server or a :class:`~openstack.compute.v2.server.Server`
                       instance that the interface belongs to.

        :returns: One
            :class:`~openstack.compute.v2.server_diagnostics.ServerDiagnostics`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found.
        """
        server_id = self._get_resource(_server.Server, server).id
        return self._get(_server_diagnostics.ServerDiagnostics,
                         server_id=server_id, requires_id=False)
