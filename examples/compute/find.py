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

import examples.connect

"""
Find a resource from the Compute service.

For a full guide see
https://docs.openstack.org/openstacksdk/latest/user/guides/compute.html
"""


def find_image(conn):
    print("Find Image:")

    image = conn.compute.find_image(examples.connect.IMAGE_NAME)

    print(image)

    return image


def find_flavor(conn):
    print("Find Flavor:")

    flavor = conn.compute.find_flavor(examples.connect.FLAVOR_NAME)

    print(flavor)

    return flavor


def find_keypair(conn):
    print("Find Keypair:")

    keypair = conn.compute.find_keypair(examples.connect.KEYPAIR_NAME)

    print(keypair)

    return keypair
