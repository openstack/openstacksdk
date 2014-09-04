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

from openstack import exceptions
from openstack.object_store import object_store_service
from openstack import resource
from openstack import utils


class Container(resource.Resource):
    base_path = "/"
    service = object_store_service.ObjectStoreService()
    id_attribute = "name"

    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    allow_head = True

    # Account data (when id=None)
    timestamp = resource.prop("x-timestamp")
    account_bytes_used = resource.prop("x-account-bytes-used")
    account_container_count = resource.prop("x-account-container-count")
    account_object_count = resource.prop("x-account-object-count")
    meta_temp_url_key = resource.prop("x-account-meta-temp-url-key")
    meta_temp_url_key_2 = resource.prop("x-account-meta-temp-url-key-2")

    # Container body data (when id=None)
    name = resource.prop("name")
    count = resource.prop("count")
    bytes = resource.prop("bytes")

    # Container metadata (when id=name)
    object_count = resource.prop("x-container-object-count")
    bytes_used = resource.prop("x-container-bytes-used")

    # Request headers (when id=None)
    newest = resource.prop("x-newest", type=bool)

    # Request headers (when id=name)
    read_ACL = resource.prop("x-container-read")
    write_ACL = resource.prop("x-container-write")
    sync_to = resource.prop("x-container-sync-to")
    sync_key = resource.prop("x-container-sync-key")
    versions_location = resource.prop("x-versions-location")
    remove_versions_location = resource.prop("x-remove-versions-location")
    content_type = resource.prop("content-type")
    detect_content_type = resource.prop("x-detect-content-type", type=bool)
    if_none_match = resource.prop("if-none-match")

    def _do_create_update(self, session, method):
        url = utils.urljoin(self.base_path, self.id)

        # Only send actual headers, not potentially set body values.
        headers = self._attrs.copy()
        for val in ("name", "count", "bytes"):
            headers.pop(val, None)

        data = method(url, service=self.service, accept=None,
                      headers=headers).headers
        self._reset_dirty()
        return data

    def create(self, session):
        if not self.allow_create:
            raise exceptions.MethodNotSupported('create')

        return self._do_create_update(session, session.put)

    def update(self, session):
        if not self.allow_update:
            raise exceptions.MethodNotSupported('update')

        return self._do_create_update(session, session.post)
