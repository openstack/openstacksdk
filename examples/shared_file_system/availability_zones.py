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
List resources from the Shared File System service.

For a full guide see
https://docs.openstack.org/openstacksdk/latest/user/guides/shared_file_system.html
"""


def list_availability_zones(conn):
    print("List Shared File System Availability Zones:")
    for az in conn.share.availability_zones():
        print(az)
