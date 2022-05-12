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


def list_share_group_snapshots(conn, **query):
    print("List all share group snapshots:")
    share_group_snapshots = conn.share.share_group_snapshots(**query)
    for share_group_snapshot in share_group_snapshots:
        print(share_group_snapshot)


def get_share_group_snapshot(conn, group_snapshot_id):
    print("Show share group snapshot with given Id:")
    share_group_snapshot = conn.share.get_share_group_snapshots(
        group_snapshot_id
    )
    print(share_group_snapshot)


def share_group_snapshot_members(conn, group_snapshot_id):
    print("Show share group snapshot members with given Id:")
    members = conn.share.share_group_snapshot_members(group_snapshot_id)
    for member in members:
        print(member)


def create_share_group_snapshot(conn, share_group_id, **attrs):
    print("Creating a share group snapshot from given attributes:")
    share_group_snapshot = conn.share.create_share_group_snapshot(
        share_group_id, **attrs
    )
    print(share_group_snapshot)


def reset_share_group_snapshot_status(conn, group_snapshot_id, status):
    print("Reseting the share group snapshot status:")
    conn.share.reset_share_group_snapshot_status(group_snapshot_id, status)


def update_share_group_snapshot(conn, group_snapshot_id, **attrs):
    print("Updating a share group snapshot with given Id:")
    share_group_snapshot = conn.share.update_share_group_snapshot(
        group_snapshot_id, **attrs
    )
    print(share_group_snapshot)


def delete_share_group_snapshot(conn, group_snapshot_id):
    print("Deleting a share group snapshot with given Id:")
    conn.share.delete_share_group_snapshot(group_snapshot_id)
