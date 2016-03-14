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

from openstack.compute.v2 import availability_zone
from openstack.compute.v2 import extension
from openstack.compute.v2 import flavor as _flavor
from openstack.compute.v2 import hypervisor as _hypervisor
from openstack.compute.v2 import image as _image
from openstack.compute.v2 import keypair as _keypair
from openstack.compute.v2 import limits
from openstack.compute.v2 import server as _server
from openstack.compute.v2 import server_group as _server_group
from openstack.compute.v2 import server_interface as _server_interface
from openstack.compute.v2 import server_ip
from openstack import proxy
from openstack import resource


class Proxy(proxy.BaseProxy):

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

    def extensions(self, **query):
        """Retrieve a generator of extensions

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of extension instances.
        :rtype: :class:`~openstack.compute.v2.extension.Extension`
        """
        return self._list(extension.Extension, paginated=False, **query)

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
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the flavors being returned.

        :returns: A generator of flavor objects
        """
        flv = _flavor.FlavorDetail if details else _flavor.Flavor
        return self._list(flv, paginated=True, **query)

    def update_flavor(self, flavor, **attrs):
        """Update a flavor

        :param flavor: Either the ID of a flavor or a
                      :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :attrs kwargs: The attributes to update on the flavor represented
                       by ``value``.

        :returns: The updated flavor
        :rtype: :class:`~openstack.compute.v2.flavor.Flavor`
        """
        return self._update(_flavor.Flavor, flavor, **attrs)

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
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of image objects
        """
        img = _image.ImageDetail if details else _image.Image
        return self._list(img, paginated=True, **query)

    def _get_base_resource(self, res, base):
        # Metadata calls for Image and Server can work for both those
        # resources but also ImageDetail and ServerDetail. If we get
        # either class, use it, otherwise create an instance of the base.
        if isinstance(res, base):
            return res
        else:
            return base({"id": res})

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
        metadata = res.get_metadata(self.session)
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
        metadata = res.set_metadata(self.session, **metadata)
        result = _image.Image.existing(id=res.id, metadata=metadata)
        return result

    def delete_image_metadata(self, image, keys):
        """Delete metadata for an image

        Note: This method will do a HTTP DELETE request for every key in keys.

        :param image: Either the ID of an image or a
                       :class:`~openstack.compute.v2.image.Image` or
                       :class:`~openstack.compute.v2.image.ImageDetail`
                       instance.
        :param list keys: The keys to delete.

        :rtype: ``None``
        """
        res = self._get_base_resource(image, _image.Image)
        return res.delete_metadata(self.session, keys)

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

    def keypairs(self, **query):
        """Return a generator of keypairs

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of keypair objects
        :rtype: :class:`~openstack.compute.v2.keypair.Keypair`
        """
        return self._list(_keypair.Keypair, paginated=False, **query)

    def update_keypair(self, keypair, **attrs):
        """Update a keypair

        :param keypair: Either the ID of a keypair or a
                        :class:`~openstack.compute.v2.keypair.Keypair`
                        instance.
        :attrs kwargs: The attributes to update on the keypair represented
                       by ``keypair``.

        :returns: The updated keypair
        :rtype: :class:`~openstack.compute.v2.keypair.Keypair`
        """
        return self._update(_keypair.Keypair, keypair, **attrs)

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

    def delete_server(self, server, ignore_missing=True):
        """Delete a server

        :param server: The value can be either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the server does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
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

    def servers(self, details=True, **query):
        """Retrieve a generator of servers

        :param bool details: When set to ``False``
                    :class:`~openstack.compute.v2.server.Server` instances
                    will be returned. The default, ``True``, will cause
                    :class:`~openstack.compute.v2.server.ServerDetail`
                    instances to be returned.
        :param kwargs \*\*query: Optional query parameters to be sent to limit
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
        srv = _server.ServerDetail if details else _server.Server

        # Server expects changes-since, but we use an underscore
        # so it can be a proper Python name.
        if "changes_since" in query:
            query["changes-since"] = query.pop("changes_since")

        return self._list(srv, paginated=True, **query)

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

    def wait_for_server(self, server, status='ACTIVE', failures=['ERROR'],
                        interval=2, wait=120):
        return resource.wait_for_status(self.session, server, status,
                                        failures, interval, wait)

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
        server_id = resource.Resource.get_id(server)
        return self._create(_server_interface.ServerInterface,
                            path_args={'server_id': server_id}, **attrs)

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
        if isinstance(server_interface, _server_interface.ServerInterface):
            server_id = server_interface.server_id
        else:
            server_id = resource.Resource.get_id(server)

        self._delete(_server_interface.ServerInterface, server_interface,
                     path_args={'server_id': server_id},
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
        if isinstance(server_interface, _server_interface.ServerInterface):
            server_id = server_interface.server_id
        else:
            server_id = resource.Resource.get_id(server)

        return self._get(_server_interface.ServerInterface, server_interface,
                         path_args={'server_id': server_id})

    def server_interfaces(self, server, **query):
        """Return a generator of server interfaces

        :param server: The server can be either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server`.
        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of ServerInterface objects
        :rtype: :class:`~openstack.compute.v2.server_interface.ServerInterface`
        """
        server_id = resource.Resource.get_id(server)
        return self._list(_server_interface.ServerInterface, paginated=False,
                          path_args={'server_id': server_id},
                          **query)

    def find_server_ip(self, name_or_id, ignore_missing=True):
        """Find a single server IP

        :param name_or_id: The name or ID of a server IP.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the resource does not exist.
                    When set to ``True``, None will be returned when
                    attempting to find a nonexistent resource.
        :returns: One :class:`~openstack.compute.v2.server_ip.ServerIP` or None
        """
        return self._find(server_ip.ServerIP, name_or_id,
                          ignore_missing=ignore_missing)

    def server_ips(self, **query):
        """Return a generator of server IPs

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of ServerIP objects
        :rtype: :class:`~openstack.compute.v2.server_ip.ServerIP`
        """
        return self._list(server_ip.ServerIP, paginated=False, **query)

    def resize_server(self, server, flavor):
        """Resize a server

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` instance.
        :param falvor: The ID or name of the flavor used to resize the server.

        :returns: None
        """
        server = _server.Server.from_id(server)
        server.resize(self.session, flavor)

    def confirm_resize_server(self, server):
        """Confirm a pending resize_server action

        :param server: Either the ID of a server or a
                      :class:`~openstack.compute.v2.server.Server` instance.

        :returns: None
        """
        server = _server.Server.from_id(server)
        server.confirm_resize(self.session)

    def revert_resize_server(self, server):
        """Cancel and revert a pending resize_server action

        :param server: Either the ID of a server or a
                      :class:`~openstack.compute.v2.server.Server` instance.

        :returns: None
        """
        server = _server.Server.from_id(server)
        server.revert_resize(self.session)

    def rebuild_server(self, server, image, name=None, admin_password=None,
                       **attrs):
        """Rebuild a server

        :param server: Either the ID of a server or a
                      :class:`~openstack.compute.v2.server.Server` instance.
        :param image: The ID or name or a
                      :class:`~openstack.compute.v2.image.Image` or full
                      URL of the image used to rebuild the server with.
        :param name: New name for the server.
        :param admin_password: New admin password for the server.
        :param kwargs \*\*attrs: The attributes to rebuild the server.

        :returns: The rebuilt server
        :rtype: :class:`~openstack.compute.v2.server.Server`
        """
        if isinstance(image, _image.Image):
            image_ref = image.id
        else:
            image_obj = self.find_image(image)
            if image_obj:
                image_ref = image_obj.id
            else:
                # the 'image' could be a full url
                image_ref = image

        server = _server.Server.from_id(server)
        return server.rebuild(self.session, name, image_ref, admin_password,
                              **attrs)

    def availability_zones(self, **query):
        """Return a generator of availability zones

        :param kwargs \*\*query: Optional query parameters to be sent
                                 to limit the resources being returned.

        :returns: A generator of availability zone
        :rtype: :class:`~openstack.compute.v2.availability_zone.
        AvailabilityZone`
        """
        return self._list(availability_zone.AvailabilityZone,
                          paginated=False, **query)

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
        metadata = res.get_metadata(self.session)
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
        metadata = res.set_metadata(self.session, **metadata)
        result = _server.Server.existing(id=res.id, metadata=metadata)
        return result

    def delete_server_metadata(self, server, keys):
        """Delete metadata for a server

        Note: This method will do a HTTP DELETE request for every key in keys.

        :param server: Either the ID of a server or a
                       :class:`~openstack.compute.v2.server.Server` or
                       :class:`~openstack.compute.v2.server.ServerDetail`
                       instance.
        :param list keys: The keys to delete

        :rtype: ``None``
        """
        res = self._get_base_resource(server, _server.Server)
        return res.delete_metadata(self.session, keys)

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

        :param kwargs \*\*query: Optional query parameters to be sent to limit
                                 the resources being returned.

        :returns: A generator of ServerGroup objects
        :rtype: :class:`~openstack.compute.v2.server_group.ServerGroup`
        """
        return self._list(_server_group.ServerGroup, paginated=False, **query)

    def hypervisors(self, **query):
        """Return a generator of hypervisor

        :returns: A generator of hypervisor
        :rtype: class: `~openstack.compute.v2.hypervisor.Hypervisor`
        """

        return self._list(_hypervisor.Hypervisor, paginated=False, **query)

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
