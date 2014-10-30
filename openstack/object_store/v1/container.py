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
    #: The transaction date and time.
    timestamp = resource.prop("x-timestamp")
    #: The total number of bytes that are stored in Object Storage for
    #: the account.
    account_bytes_used = resource.prop("x-account-bytes-used")
    #: The number of containers.
    account_container_count = resource.prop("x-account-container-count")
    #: The number of objects in the account.
    account_object_count = resource.prop("x-account-object-count")
    #: The secret key value for temporary URLs. If not set,
    #: this header is not returned by this operation.
    meta_temp_url_key = resource.prop("x-account-meta-temp-url-key")
    #: A second secret key value for temporary URLs. If not set,
    #: this header is not returned by this operation.
    meta_temp_url_key_2 = resource.prop("x-account-meta-temp-url-key-2")

    # Container body data (when id=None)
    #: The name of the container.
    name = resource.prop("name")
    #: The number of objects in the container.
    count = resource.prop("count")
    #: The total number of bytes that are stored in Object Storage
    #: for the container.
    bytes = resource.prop("bytes")

    # Container metadata (when id=name)
    #: The number of objects.
    object_count = resource.prop("x-container-object-count")
    #: The count of bytes used in total.
    bytes_used = resource.prop("x-container-bytes-used")

    # Request headers (when id=None)
    #: If set to True, Object Storage queries all replicas to return the
    #: most recent one. If you omit this header, Object Storage responds
    #: faster after it finds one valid replica. Because setting this
    #: header to True is more expensive for the back end, use it only
    #: when it is absolutely needed.
    newest = resource.prop("x-newest", type=bool)

    # Request headers (when id=name)
    #: The ACL that grants read access. If not set, this header is not
    #: returned by this operation.
    read_ACL = resource.prop("x-container-read")
    #: The ACL that grants write access. If not set, this header is not
    #: returned by this operation.
    write_ACL = resource.prop("x-container-write")
    #: The destination for container synchronization. If not set,
    #: this header is not returned by this operation.
    sync_to = resource.prop("x-container-sync-to")
    #: The secret key for container synchronization. If not set,
    #: this header is not returned by this operation.
    sync_key = resource.prop("x-container-sync-key")
    #: Enables versioning on this container. The value is the name
    #: of another container. You must UTF-8-encode and then URL-encode
    #: the name before you include it in the header. To disable
    #: versioning, set the header to an empty string.
    versions_location = resource.prop("x-versions-location")
    #: Set to any value to disable versioning.
    remove_versions_location = resource.prop("x-remove-versions-location")
    #: Changes the MIME type for the object.
    content_type = resource.prop("content-type")
    #: If set to true, Object Storage guesses the content type based
    #: on the file extension and ignores the value sent in the
    #: Content-Type header, if present.
    detect_content_type = resource.prop("x-detect-content-type", type=bool)
    #: In combination with Expect: 100-Continue, specify an
    #: "If-None-Match: \*" header to query whether the server already
    #: has a copy of the object before any data is sent.
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
