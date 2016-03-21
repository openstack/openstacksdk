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

from examples.connect import FLAVOR_NAME
from examples.connect import IMAGE_NAME
from examples.connect import NETWORK_NAME
from examples.connect import SERVER_NAME

"""
Managing profiles in the Cluster service.

For a full guide see
http://developer.openstack.org/sdks/python/openstacksdk/users/guides/cluster.html
"""


def list_profiles(conn):
    print("List Profiles:")

    for profile in conn.cluster.profiles():
        print(profile.to_dict())

    for profile in conn.cluster.profiles(sort='name:asc'):
        print(profile.to_dict())


def create_profile(conn):
    print("Create Profile:")

    spec = {
        'profile': 'os.nova.server',
        'version': 1.0,
        'properties': {
            'name': SERVER_NAME,
            'flavor': FLAVOR_NAME,
            'image': IMAGE_NAME,
            'networks': {
                'network': NETWORK_NAME
            }
        }
    }

    profile = conn.cluster.create_profile('os_server', spec)
    print(profile.to_dict())


def get_profile(conn):
    print("Get Profile:")

    profile = conn.cluster.get_profile('os_server')
    print(profile.to_dict())


def find_profile(conn):
    print("Find Profile:")

    profile = conn.cluster.find_profile('os_server')
    print(profile.to_dict())


def update_profile(conn):
    print("Update Profile:")

    profile = conn.cluster.update_profile('os_server', name='old_server')
    print(profile.to_dict())


def delete_profile(conn):
    print("Delete Profile:")

    conn.cluster.delete_profile('os_server')

    print("Profile deleted.")
