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


def list_share_metadata(conn, share_id):
    # Method returns the entire share with the metadata inside it.
    returned_share = conn.get_share_metadata(share_id)

    # Access metadata of share
    metadata = returned_share['metadata']

    print("List All Share Metadata:")
    for meta_key in metadata:
        print(f"{meta_key}={metadata[meta_key]}")


def get_share_metadata_item(conn, share_id, key):
    # Method returns the entire share with the metadata inside it.
    returned_share = conn.get_share_metadata_item(share_id, key)

    # Access metadata of share
    metadata = returned_share['metadata']

    print("Get share metadata item given item key and share id:")
    print(metadata[key])


def create_share_metadata(conn, share_id, metadata):
    # Method returns the entire share with the metadata inside it.
    created_share = conn.create_share_metadata(share_id, metadata)

    # Access metadata of share
    metadata = created_share['metadata']

    print("Metadata created for given share:")
    print(metadata)


def update_share_metadata(conn, share_id, metadata):
    # Method returns the entire share with the metadata inside it.
    updated_share = conn.update_share_metadata(share_id, metadata, True)

    # Access metadata of share
    metadata = updated_share['metadata']

    print("Updated metadata for given share:")
    print(metadata)


def delete_share_metadata(conn, share_id, keys):
    # Method doesn't return anything.
    conn.delete_share_metadata(share_id, keys)
