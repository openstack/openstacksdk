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

import os

from examples.connect import FLAVOR_NAME
from examples.connect import IMAGE_NAME
from examples.connect import KEYPAIR_NAME
from examples.connect import NETWORK_NAME
from examples.connect import PRIVATE_KEYPAIR_FILE

"""
Create resources with the Compute service.

For a full guide see TODO(etoews):link to docs on developer.openstack.org
"""


def create_server(conn):
    print("Create Server:")

    image = conn.compute.find_image(IMAGE_NAME)
    flavor = conn.compute.find_flavor(FLAVOR_NAME)
    network = conn.network.find_network(NETWORK_NAME)

    if not conn.compute.find_keypair(KEYPAIR_NAME):
        keypair = conn.compute.create_keypair(name=KEYPAIR_NAME)

        with open(PRIVATE_KEYPAIR_FILE, 'w') as f:
            f.write("%s" % keypair.private_key)

        os.chmod(PRIVATE_KEYPAIR_FILE, 0o400)

    server = conn.compute.create_server(
        name='openstacksdk-example', image=image, flavor=flavor,
        networks=[{"uuid": network.id}], key_name=KEYPAIR_NAME)

    server = conn.compute.wait_for_server(server)

    print("ssh -i {key} root@{ip}".format(
        key=PRIVATE_KEYPAIR_FILE,
        ip=server.access_ipv4))
