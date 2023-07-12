# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def resize_share(conn, share_id, share_size):
    # Be explicit about not wanting to use force if the share
    # will be extended.
    use_force = False
    print('Resize the share to the given size:')
    conn.share.resize_share(share_id, share_size, use_force)


def resize_shares_without_shrink(conn, min_size):
    # Sometimes, extending shares without shrinking
    # them (effectively setting a min size) is desirable.

    # Get list of shares from the connection.
    shares = conn.share.shares()

    # Loop over the shares:
    for share in shares:
        # Extend shares smaller than min_size to min_size,
        # but don't shrink shares larger than min_size.
        conn.share.resize_share(share.id, min_size, no_shrink=True)


def manage_share(conn, protocol, export_path, service_host, **params):
    # Manage a share with the given protocol, export path, service host, and
    # optional additional parameters
    managed_share = conn.share.manage_share(
        protocol, export_path, service_host, **params
    )

    # Can get the ID of the share, which is now being managed with Manila
    managed_share_id = managed_share.id
    print("The ID of the share which was managed: %s", managed_share_id)


def unmanage_share(conn, share_id):
    # Unmanage the share with the given share ID
    conn.share.unmanage_share(share_id)

    try:
        # Getting the share will raise an exception as it has been unmanaged
        conn.share.get_share(share_id)
    except Exception:
        pass
