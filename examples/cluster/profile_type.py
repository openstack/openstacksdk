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
Managing profile types in the Cluster service.

For a full guide see
http://developer.openstack.org/sdks/python/openstacksdk/users/guides/cluster.html
"""


def list_profile_types(conn):
    print("List Profile Types:")

    for pt in conn.cluster.profile_types():
        print(pt.to_dict())


def get_profile_type(conn):
    print("Get Profile Type:")

    pt = conn.cluster.get_profile_type('os.nova.server-1.0')

    print(pt.to_dict())
