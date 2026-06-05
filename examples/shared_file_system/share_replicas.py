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


def list_share_replicas(conn, **attrs):
    print("List share replicas for the shared file system:")
    for sr in conn.share.share_replicas(**attrs):
        print(sr)


def create_share_replica(conn, share_id, **attrs):
    print("Creating share replica:")
    share_replica = conn.share.create_share_replica(share_id, **attrs)
    print(share_replica)


def get_share_replica(conn, share_replica_id):
    print("Getting share replica with give Id:")
    share_replica = conn.share.share_replica(share_replica_id)
    print(share_replica)


def delete_share_replica(conn, share_replica_id):
    print("Deleting share replica with give Id:")
    conn.share.delete_share_replica(share_replica_id)


def reset_status_share_replica(conn, share_replica_id, status):
    print("Resetting status for given share replica Id:")
    conn.share.share_replica_reset_status(share_replica_id, status)


def reset_replica_state_share_replica(conn, share_replica_id, reset_state):
    print("Resetting replica state for given share replica Id:")
    conn.share.share_replica_reset_replica_state(share_replica_id, reset_state)


def force_delete_share_replica(conn, share_replica_id):
    print("Force deleting the share replica for the given Id:")
    conn.share.share_replica_force_delete(share_replica_id)


def promote_share_replica(conn, share_replica_id):
    print("Promoting share replica with given Id:")
    conn.share.share_replica_promote(share_replica_id)


def resync_share_replica(conn, share_replica_id):
    print("Resyncing share replica with given Id:")
    conn.share.share_replica_resync(share_replica_id)
