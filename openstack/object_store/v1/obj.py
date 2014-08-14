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


class Object(resource.Resource):
    base_path = "/%(container)s"
    service = object_store_service.ObjectStoreService()
    id_attribute = "name"

    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    allow_head = True

    # URL parameters
    container = resource.prop("container")
    name = resource.prop("name")

    # Object details
    hash = resource.prop("hash")
    bytes = resource.prop("bytes")

    # Headers for HEAD and GET requests
    auth_token = resource.prop("x-auth-token")
    newest = resource.prop("x-newest", type=bool)
    range = resource.prop("range", type=dict)
    if_match = resource.prop("if-match", type=dict)
    if_none_match = resource.prop("if-none-match", type=dict)
    if_modified_since = resource.prop("if-modified-since", type=dict)
    if_unmodified_since = resource.prop("if-unmodified-since", type=dict)

    # Query parameters
    signature = resource.prop("signature")
    expires = resource.prop("expires")
    multipart_manifest = resource.prop("multipart-manifest")

    # Response headers from HEAD and GET
    content_length = resource.prop("content-length")
    content_type = resource.prop("content-type")
    accept_ranges = resource.prop("accept-ranges")
    last_modified = resource.prop("last-modified")
    etag = resource.prop("etag")
    is_static_large_object = resource.prop("x-static-large-object")
    date = resource.prop("date")
    content_encoding = resource.prop("content-encoding")
    content_disposition = resource.prop("content-disposition")
    delete_at = resource.prop("x-delete-at", type=int)
    object_manifest = resource.prop("x-object-manifest")
    timestamp = resource.prop("x-timestamp")

    # Headers for PUT and POST requests
    transfer_encoding = resource.prop("transfer-encoding")
    detect_content_type = resource.prop("x-detect-content-type", type=bool)
    copy_from = resource.prop("x-copy-from")
    delete_after = resource.prop("x-delete-after", type=int)

    def get(self, session):
        if not self.allow_retrieve:
            raise exceptions.MethodNotSupported('retrieve')

        # When joining the base_path part and the id part, base_path's
        # leading slash gets dropped off here. Putting an empty leading value
        # in front of it causes it to get joined and replaced.
        url = utils.urljoin("", self.base_path % self, self.id)

        # Only send actual headers, not potentially set body values and
        # query parameters.
        headers = self._attrs.copy()
        for val in ("container", "name", "hash", "bytes", "signature",
                    "expires", "multipart_manifest"):
            headers.pop(val, None)

        resp = session.get(url, service=self.service, accept="bytes",
                           headers=headers).content

        return resp
