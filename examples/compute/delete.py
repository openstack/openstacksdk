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

import errno
import os

from examples.connect import KEYPAIR_NAME
from examples.connect import PRIVATE_KEYPAIR_FILE
from examples.connect import SERVER_NAME

"""
Delete resources with the Compute service.

For a full guide see TODO(etoews):link to docs on developer.openstack.org
"""


def delete_keypair(conn):
    print("Delete Key Pair:")

    keypair = conn.compute.find_keypair(KEYPAIR_NAME)

    try:
        os.remove(PRIVATE_KEYPAIR_FILE)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise e

    print(keypair)

    conn.compute.delete_keypair(keypair)


def delete_server(conn):
    print("Delete Server:")

    server = conn.compute.find_server(SERVER_NAME)

    print(server)

    conn.compute.delete_server(server)
