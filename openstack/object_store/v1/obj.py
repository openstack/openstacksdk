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
    #: The unique name for the container.
    container = resource.prop("container")
    #: The unique name for the object.
    name = resource.prop("name")

    # Object details
    hash = resource.prop("hash")
    bytes = resource.prop("bytes")

    # Headers for HEAD and GET requests
    #: Authentication token.
    auth_token = resource.prop("x-auth-token")
    #: If set to True, Object Storage queries all replicas to return
    #: the most recent one. If you omit this header, Object Storage
    #: responds faster after it finds one valid replica. Because
    #: setting this header to True is more expensive for the back end,
    #: use it only when it is absolutely needed.
    newest = resource.prop("x-newest", type=bool)
    #: TODO(briancurtin) there's a lot of content here...
    range = resource.prop("range", type=dict)
    #: See http://www.ietf.org/rfc/rfc2616.txt.
    if_match = resource.prop("if-match", type=dict)
    #: In combination with Expect: 100-Continue, specify an
    #: "If-None-Match: \*" header to query whether the server already
    #: has a copy of the object before any data is sent.
    if_none_match = resource.prop("if-none-match", type=dict)
    #: See http://www.ietf.org/rfc/rfc2616.txt.
    if_modified_since = resource.prop("if-modified-since", type=dict)
    #: See http://www.ietf.org/rfc/rfc2616.txt.
    if_unmodified_since = resource.prop("if-unmodified-since", type=dict)

    # Query parameters
    #: Used with temporary URLs to sign the request. For more
    #: information about temporary URLs, see OpenStack Object Storage
    #: API v1 Reference.
    signature = resource.prop("signature")
    #: Used with temporary URLs to specify the expiry time of the
    #: signature. For more information about temporary URLs, see
    #: OpenStack Object Storage API v1 Reference.
    expires = resource.prop("expires")
    #: If you include the multipart-manifest=get query parameter and
    #: the object is a large object, the object contents are not
    #: returned. Instead, the manifest is returned in the
    #: X-Object-Manifest response header for dynamic large objects
    #: or in the response body for static large objects.
    multipart_manifest = resource.prop("multipart-manifest")

    # Response headers from HEAD and GET
    #: HEAD operations do not return content. However, in this
    #: operation the value in the Content-Length header is not the
    #: size of the response body. Instead it contains the size of
    #: the object, in bytes.
    content_length = resource.prop("content-length")
    #: The MIME type of the object.
    content_type = resource.prop("content_type", alias="content-type")
    #: The type of ranges that the object accepts.
    accept_ranges = resource.prop("accept-ranges")
    #: The date and time that the object was created or the last
    #: time that the metadata was changed.
    last_modified = resource.prop("last_modified", alias="last-modified")
    #: For objects smaller than 5 GB, this value is the MD5 checksum
    #: of the object content. The value is not quoted.
    #: For manifest objects, this value is the MD5 checksum of the
    #: concatenated string of MD5 checksums and ETags for each of
    #: the segments in the manifest, and not the MD5 checksum of
    #: the content that was downloaded. Also the value is enclosed
    #: in double-quote characters.
    #: You are strongly recommended to compute the MD5 checksum of
    #: the response body as it is received and compare this value
    #: with the one in the ETag header. If they differ, the content
    #: was corrupted, so retry the operation.
    etag = resource.prop("etag")
    #: Set to True if this object is a static large object manifest object.
    is_static_large_object = resource.prop("x-static-large-object")
    #: The transaction date and time.
    date = resource.prop("date")
    #: If set, the value of the Content-Encoding metadata.
    #: If not set, this header is not returned by this operation.
    content_encoding = resource.prop("content-encoding")
    #: If set, specifies the override behavior for the browser.
    #: For example, this header might specify that the browser use
    #: a download program to save this file rather than show the file,
    #: which is the default.
    #: If not set, this header is not returned by this operation.
    content_disposition = resource.prop("content-disposition")
    #: If set, the time when the object will be deleted by the system
    #: in the format of a UNIX Epoch timestamp.
    #: If not set, this header is not returned by this operation.
    delete_at = resource.prop("x-delete-at", type=int)
    #: If set, to this is a dynamic large object manifest object.
    #: The value is the container and object name prefix of the
    #: segment objects in the form container/prefix.
    object_manifest = resource.prop("x-object-manifest")
    #: The UNIX timestamp of the transaction.
    timestamp = resource.prop("x-timestamp")

    # Headers for PUT and POST requests
    #: Set to chunked to enable chunked transfer encoding. If used,
    #: do not set the Content-Length header to a non-zero value.
    transfer_encoding = resource.prop("transfer-encoding")
    #: If set to true, Object Storage guesses the content type based
    #: on the file extension and ignores the value sent in the
    #: Content-Type header, if present.
    detect_content_type = resource.prop("x-detect-content-type", type=bool)
    #: If set, this is the name of an object used to create the new
    #: object by copying the X-Copy-From object. The value is in form
    #: {container}/{object}. You must UTF-8-encode and then URL-encode
    #: the names of the container and object before you include them
    #: in the header.
    #: Using PUT with X-Copy-From has the same effect as using the
    #: COPY operation to copy an object.
    copy_from = resource.prop("x-copy-from")
    #: Specifies the number of seconds after which the object is
    #: removed. Internally, the Object Storage system stores this
    #: value in the X-Delete-At metadata item.
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

    def create(self, session, data=None):
        """Create a remote resource from this instance."""
        if not self.allow_create:
            raise exceptions.MethodNotSupported('create')

        url = utils.urljoin("", self.base_path % self, self.id)

        if data is not None:
            resp = session.put(url, service=self.service, data=data,
                               accept="bytes").headers
        else:
            resp = session.post(url, service=self.service, data=None,
                                accept=None).headers

        self._attrs.update(resp)
