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


class Proxy(proxy.BaseProxy):

    def find_extension(self, name_or_id):
        return extension.Extension.find(self.session, name_or_id)

    def list_extensions(self):
        return extension.Extension.list(self.session)

    def find_flavor(self, name_or_id):
        return flavor.Flavor.find(self.session, name_or_id)

    def create_flavor(self, **data):
        return flavor.Flavor(data).create(self.session)

    def delete_flavor(self, **data):
        flavor.Flavor(data).delete(self.session)

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

    def update_flavor(self, **data):
        return flavor.Flavor(data).update(self.session)

    def delete_image(self, **data):
        image.Image(data).delete(self.session)

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

    def create_keypair(self, **data):
        return keypair.Keypair(data).create(self.session)

    def delete_keypair(self, **data):
        keypair.Keypair(data).delete(self.session)

    def get_keypair(self, **data):
        return keypair.Keypair(data).get(self.session)

    def find_keypair(self, name_or_id):
        return keypair.Keypair.find(self.session, name_or_id)

    def list_keypairs(self, **params):
        return keypair.Keypair.list(self.session, **params)

    def update_keypair(self, **data):
        return keypair.Keypair(data).update(self.session)

    def limits(self):
        """Retrieve limits that are applied to the project's account

        :returns: A Limits object, including both
                  :class:`~openstack.compute.v2.limits.AbsoluteLimits` and
                  :class:`~openstack.compute.v2.limits.RateLimits`
        :rtype: :class:`~openstack.compute.v2.limits.Limits`
        """
        return limits.Limits().get(self.session)

    def create_server(self, **data):
        return server.Server(data).create(self.session)

    def delete_server(self, **data):
        server.Server(data).delete(self.session)

    def find_server(self, name_or_id):
        return server.Server.find(self.session, name_or_id)

    def get_server(self, **data):
        return server.Server(data).get(self.session)

    def list_servers(self, details=True):
        srv = server.ServerDetail if details else server.Server
        return srv.list(self.session, paginated=True)

    def update_server(self, **data):
        return server.Server(data).update(self.session)

    def wait_for_status(self, server, status='ACTIVE', failures=['ERROR'],
                        interval=2, wait=120):
        return server.wait_for_status(self.session, status, failures, interval,
                                      wait)

    def create_server_interface(self, **data):
        return server_interface.ServerInterface(data).create(self.session)

    def delete_server_interface(self, **data):
        server_interface.ServerInterface(data).delete(self.session)

    def find_server_interface(self, name_or_id):
        return server_interface.ServerInterface.find(self.session, name_or_id)

    def get_server_interface(self, **data):
        return server_interface.ServerInterface(data).get(self.session)

    def list_server_interfaces(self):
        return server_interface.ServerInterface.list(self.session)

    def update_server_interface(self, **data):
        return server_interface.ServerInterface(data).update(self.session)

    def find_server_ip(self, name_or_id):
        return server_ip.ServerIP.find(self.session, name_or_id)

    def list_server_ips(self):
        return server_ip.ServerIP.list(self.session)
