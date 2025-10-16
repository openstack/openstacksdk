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
Find resources from the Key Manager service.

For a full guide see
https://docs.openstack.org/openstacksdk/latest/user/guides/key_manager.html
"""


def find_secret(conn, name_or_id):
    print(f"Find Secret: {name_or_id}")

    secret = conn.key_manager.find_secret(name_or_id)

    if secret:
        print(secret)
        return secret
    else:
        print("Secret not found")
        return None
