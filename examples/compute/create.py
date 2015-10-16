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

"""
Create resources with the Compute service.

For a full guide see TODO(etoews):link to docs on developer.openstack.org
"""


def create_server(conn, name, image, flavor, network):
    print("Create Server:")

    server = conn.compute.create_server(name=name, image=image,
                                        flavor=flavor,
                                        networks=[{"uuid": network.id}])
    conn.compute.wait_for_server(server)

    print(server)
