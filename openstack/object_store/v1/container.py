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

from openstack.object_store import object_store_service
from openstack import resource


class Container(resource.Resource):
    base_path = "/"
    service = object_store_service.ObjectStoreService()

    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    allow_head = True

    # Account data (from headers when id=None)
    timestamp = resource.prop("x-timestamp")
    account_bytes_used = resource.prop("x-account-bytes-used")
    account_container_count = resource.prop("x-account-container-count")
    account_object_count = resource.prop("x-account-object-count")
    meta_temp_url_key = resource.prop("x-account-meta-temp-url-key")
    meta_temp_url_key_2 = resource.prop("x-account-meta-temp-url-key-2")

    # Container data (from list when id=None)
    name = resource.prop("name")
    count = resource.prop("count")
    bytes = resource.prop("bytes")

    # Container metadata (when id=name)
    object_count = resource.prop("x-container-object-count")
    bytes_used = resource.prop("x-container-bytes-used")

    # Optional Container metadata (from head when id=name)
    can_read = resource.prop("x-container-read")
    can_write = resource.prop("x-container-write")
    sync_to = resource.prop("x-container-sync-to")
    sync_key = resource.prop("x-container-sync-key")
    versions_location = resource.prop("x-versions-location")

    @property
    def id(self):
        try:
            val = self.name
        except AttributeError:
            val = None
        return val
