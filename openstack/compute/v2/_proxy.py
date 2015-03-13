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

from openstack.compute.v2 import extension
from openstack.compute.v2 import flavor
from openstack.compute.v2 import image
from openstack.compute.v2 import keypair
from openstack.compute.v2 import limits
from openstack.compute.v2 import server
from openstack.compute.v2 import server_interface
from openstack.compute.v2 import server_ip
from openstack import proxy
from openstack import resource


class Proxy(proxy.BaseProxy):

    def find_extension(self, name_or_id):
        return extension.Extension.find(self.session, name_or_id)

    def list_extensions(self):
        return extension.Extension.list(self.session)

    def find_flavor(self, name_or_id):
        return flavor.Flavor.find(self.session, name_or_id)

    def create_flavor(self, **attrs):
        """Create a new flavor from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.compute.v2.flavor.Flavor`,
                           comprised of the properties on the Flavor class.

        :returns: The results of server creation
        :rtype: :class:`~openstack.compute.v2.flavor.Flavor`
        """
        return self._create(flavor.Flavor, **attrs)

    def delete_flavor(self, value, ignore_missing=True):
        """Delete a flavor

        :param value: The value can be either the ID of a flavor or a
                      :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the flavor does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(flavor.Flavor, value, ignore_missing)

    def get_flavor(self, **data):
        return flavor.Flavor(data).get(self.session)

    def list_flavors(self, details=True, **params):
        """Return a generator of flavors

        :param bool details: When ``True``, returns
            :class:`~openstack.compute.v2.flavor.FlavorDetail` objects,
            otherwise :class:`~openstack.compute.v2.flavor.Flavor`.
            *Default: ``True``*

        :returns: A generator of flavor objects
        """
        flv = flavor.FlavorDetail if details else flavor.Flavor
        return flv.list(self.session, **params)

    def update_flavor(self, value, **attrs):
        """Update a flavor

        :param value: Either the id of a flavor or a
                      :class:`~openstack.compute.v2.flavor.Flavor` instance.
        :attrs kwargs: The attributes to update on the flavor represented
                       by ``value``.

        :returns: The updated flavor
        :rtype: :class:`~openstack.compute.v2.flavor.Flavor`
        """
        return self._update(flavor.Flavor, value, **attrs)

    def delete_image(self, value, ignore_missing=True):
        """Delete an image

        :param value: The value can be either the ID of an image or a
                      :class:`~openstack.compute.v2.image.Image` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the image does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(image.Image, value, ignore_missing)

    def find_image(self, name_or_id):
        return image.Image.find(self.session, name_or_id)

    def get_image(self, **data):
        return image.Image(data).get(self.session)

    def list_images(self, details=True):
        """Return a generator of images

        :param bool details: When ``True``, returns
            :class:`~openstack.compute.v2.image.ImageDetail` objects,
            otherwise :class:`~openstack.compute.v2.image.Image`.
            *Default: ``True``*

        :returns: A generator of image objects
        """
        img = image.ImageDetail if details else image.Image
        return img.list(self.session, paginated=True)

    def create_keypair(self, **attrs):
        """Create a new keypair from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.compute.v2.keypair.Keypair`,
                           comprised of the properties on the Keypair class.

        :returns: The results of server creation
        :rtype: :class:`~openstack.compute.v2.keypair.Keypair`
        """
        return self._create(keypair.Keypair, **attrs)

    def delete_keypair(self, value, ignore_missing=True):
        """Delete a keypair

        :param value: The value can be either the ID of a keypair or a
                      :class:`~openstack.compute.v2.keypair.Keypair` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the keypair does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(keypair.Keypair, value, ignore_missing)

    def get_keypair(self, **data):
        return keypair.Keypair(data).get(self.session)

    def find_keypair(self, name_or_id):
        return keypair.Keypair.find(self.session, name_or_id)

    def list_keypairs(self, **params):
        return keypair.Keypair.list(self.session, **params)

    def update_keypair(self, value, **attrs):
        """Update a keypair

        :param value: Either the id of a keypair or a
                      :class:`~openstack.compute.v2.keypair.Keypair` instance.
        :attrs kwargs: The attributes to update on the keypair represented
                       by ``value``.

        :returns: The updated keypair
        :rtype: :class:`~openstack.compute.v2.keypair.Keypair`
        """
        return self._update(keypair.Keypair, value, **attrs)

    def limits(self):
        """Retrieve limits that are applied to the project's account

        :returns: A Limits object, including both
                  :class:`~openstack.compute.v2.limits.AbsoluteLimits` and
                  :class:`~openstack.compute.v2.limits.RateLimits`
        :rtype: :class:`~openstack.compute.v2.limits.Limits`
        """
        return limits.Limits().get(self.session)

    def create_server(self, **attrs):
        """Create a new server from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.compute.v2.server.Server`,
                           comprised of the properties on the Server class.

        :returns: The results of server creation
        :rtype: :class:`~openstack.compute.v2.server.Server`
        """
        return self._create(server.Server, **attrs)

    def delete_server(self, value, ignore_missing=True):
        """Delete a server

        :param value: The value can be either the ID of a server or a
                      :class:`~openstack.compute.v2.server.Server` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the server does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(server.Server, value, ignore_missing)

    def find_server(self, name_or_id):
        return server.Server.find(self.session, name_or_id)

    def get_server(self, value):
        """Get a single server

        :param value: The value can be the ID of a server or a
                      :class:`~openstack.compute.v2.server.Server` instance.

        :returns: One :class:`~openstack.compute.v2.server.Server`
        :raises: :class:`~openstack.exceptions.ResourceNotFound`
                 when no resource can be found for this name or id.
        """
        return self._get(server.Server, value)

    def list_servers(self, details=True):
        srv = server.ServerDetail if details else server.Server
        return srv.list(self.session, paginated=True)

    def update_server(self, value, **attrs):
        """Update a server

        :param value: Either the id of a server or a
                      :class:`~openstack.compute.v2.server.Server` instance.
        :attrs kwargs: The attributes to update on the server represented
                       by ``value``.

        :returns: The updated server
        :rtype: :class:`~openstack.compute.v2.server.Server`
        """
        return self._update(server.Server, value, **attrs)

    def wait_for_server(self, value, status='ACTIVE', failures=['ERROR'],
                        interval=2, wait=120):
        return resource.wait_for_status(self.session, value, status,
                                        failures, interval, wait)

    def create_server_interface(self, **attrs):
        """Create a new server interface from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.compute.v2.server_interface.ServerInterface`,
            comprised of the properties on the ServerInterface class.

        :returns: The results of server creation
        :rtype: :class:`~openstack.compute.v2.server_interface.ServerInterface`
        """
        return self._create(server_interface.ServerInterface, **attrs)

    def delete_server_interface(self, value, ignore_missing=True):
        """Delete a server interface

        :param value: The value can be either the ID of a server or a
               :class:`~openstack.compute.v2.server_interface.ServerInterface`
               instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the server interface does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent server.

        :returns: ``None``
        """
        self._delete(server_interface.ServerInterface, value, ignore_missing)

    def find_server_interface(self, name_or_id):
        return server_interface.ServerInterface.find(self.session, name_or_id)

    def get_server_interface(self, **data):
        return server_interface.ServerInterface(data).get(self.session)

    def list_server_interfaces(self):
        return server_interface.ServerInterface.list(self.session)

    def update_server_interface(self, value, **attrs):
        """Update a server interface

        :param value: Either the id of a server interface or a
                      :class:
                      `~openstack.compute.v2.server_interface.ServerInterface`
                      instance.
        :attrs kwargs: The attributes to update on the server interface
                       represented by ``value``.

        :returns: The updated server interface
        :rtype: :class:`~openstack.compute.v2.server_interface.ServerInterface`
        """
        return self._update(server_interface.ServerInterface, value, **attrs)

    def find_server_ip(self, name_or_id):
        return server_ip.ServerIP.find(self.session, name_or_id)

    def list_server_ips(self):
        return server_ip.ServerIP.list(self.session)
