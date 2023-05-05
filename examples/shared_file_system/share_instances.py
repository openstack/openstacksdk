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


def share_instances(conn, **query):
    print('List all share instances:')
    for si in conn.share.share_instances(**query):
        print(si)


def get_share_instance(conn, share_instance_id):
    print('Get share instance with given Id:')
    share_instance = conn.share.get_share_instance(share_instance_id)
    print(share_instance)


def reset_share_instance_status(conn, share_instance_id, status):
    print(
        'Reset the status of the share instance with the given '
        'share_instance_id to the given status'
    )
    conn.share.reset_share_instance_status(share_instance_id, status)


def delete_share_instance(conn, share_instance_id):
    print('Force-delete the share instance with the given share_instance_id')
    conn.share.delete_share_instance(share_instance_id)
