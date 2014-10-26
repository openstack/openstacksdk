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

from openstack.compute.v2 import flavor
from openstack.compute.v2 import keypairs
from openstack.compute.v2 import server


class Proxy(object):

    def __init__(self, session):
        self.session = session

    def create_flavor(self, **data):
        return flavor.Flavor(data).create(self.session)

    def delete_flavor(self, **data):
        flavor.Flavor(data).delete(self.session)

    def find_flavor(self, name_or_id):
        return flavor.Flavor.find(self.session, name_or_id)

    def get_flavor(self, **data):
        return flavor.Flavor(data).get(self.session)

    def list_flavors(self, **params):
        return flavor.Flavor.list(self.session, **params)

    def update_flavor(self, **data):
        return flavor.Flavor(data).update(self.session)

    def create_keypair(self, **data):
        return keypairs.Keypairs(data).create(self.session)

    def delete_keypair(self, **data):
        keypairs.Keypairs(data).delete(self.session)

    def get_keypair(self, **data):
        return keypairs.Keypairs(data).get(self.session)

    def find_keypair(self, name_or_id):
        return keypairs.Keypairs.find(self.session, name_or_id)

    def list_keypairs(self, **params):
        return keypairs.Keypairs.list(self.session, **params)

    def update_keypair(self, **data):
        return keypairs.Keypairs(data).update(self.session)

    def create_server(self, **data):
        return server.Server(data).create(self.session)

    def delete_server(self, **data):
        server.Server(data).delete(self.session)

    def find_server(self, name_or_id):
        return server.Server.find(self.session, name_or_id)

    def get_server(self, **data):
        return server.Server(data).get(self.session)

    def list_servers(self):
        return server.Server.list(self.session)

    def update_server(self, **data):
        return server.Server(data).update(self.session)

    def wait_for_status(self, server, status='ACTIVE', interval=2, wait=120):
        return server.wait_for_status(self.session, status, interval, wait)
