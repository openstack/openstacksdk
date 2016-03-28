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

import copy

from openstack import format
from openstack.object_store import object_store_service
from openstack.object_store.v1 import _base
from openstack import resource


class Object(_base.BaseResource):
    _custom_metadata_prefix = "X-Object-Meta-"
    _system_metadata = {
        "content_disposition": "content-disposition",
        "content_encoding": "content-encoding",
        "content_type": "content-type",
        "delete_after": "x-delete-after",
        "delete_at": "x-delete-at",
        "is_content_type_detected": "x-detect-content-type",
    }

    base_path = "/%(container)s"
    service = object_store_service.ObjectStoreService()
    id_attribute = "name"

    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    allow_head = True

    # Data to be passed during a POST call to create an object on the server.
    data = None

    # URL parameters
    #: The unique name for the container.
    container = resource.prop("container")
    #: The unique name for the object.
    name = resource.prop("name")

    # Object details
    hash = resource.prop("hash")
    bytes = resource.prop("bytes")

    # Headers for HEAD and GET requests
    #: If set to True, Object Storage queries all replicas to return
    #: the most recent one. If you omit this header, Object Storage
    #: responds faster after it finds one valid replica. Because
    #: setting this header to True is more expensive for the back end,
    #: use it only when it is absolutely needed. *Type: bool*
    is_newest = resource.header("x-newest", type=bool)
    #: TODO(briancurtin) there's a lot of content here...
    range = resource.header("range", type=dict)
    #: See http://www.ietf.org/rfc/rfc2616.txt.
    if_match = resource.header("if-match", type=dict)
    #: In combination with Expect: 100-Continue, specify an
    #: "If-None-Match: \*" header to query whether the server already
    #: has a copy of the object before any data is sent.
    if_none_match = resource.header("if-none-match", type=dict)
    #: See http://www.ietf.org/rfc/rfc2616.txt.
    if_modified_since = resource.header("if-modified-since", type=dict)
    #: See http://www.ietf.org/rfc/rfc2616.txt.
    if_unmodified_since = resource.header("if-unmodified-since", type=dict)

    # Query parameters
    #: Used with temporary URLs to sign the request. For more
    #: information about temporary URLs, see OpenStack Object Storage
    #: API v1 Reference.
    signature = resource.header("signature")
    #: Used with temporary URLs to specify the expiry time of the
    #: signature. For more information about temporary URLs, see
    #: OpenStack Object Storage API v1 Reference.
    #: *Type: datetime object parsed from ISO 8601 formatted string*
    expires_at = resource.header("expires", type=format.ISO8601)
    #: If you include the multipart-manifest=get query parameter and
    #: the object is a large object, the object contents are not
    #: returned. Instead, the manifest is returned in the
    #: X-Object-Manifest response header for dynamic large objects
    #: or in the response body for static large objects.
    multipart_manifest = resource.header("multipart-manifest")

    # Response headers from HEAD and GET
    #: HEAD operations do not return content. However, in this
    #: operation the value in the Content-Length header is not the
    #: size of the response body. Instead it contains the size of
    #: the object, in bytes.
    content_length = resource.header("content-length")
    #: The MIME type of the object.
    content_type = resource.header("content-type")
    #: The type of ranges that the object accepts.
    accept_ranges = resource.header("accept-ranges")
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
    etag = resource.header("etag")
    #: Set to True if this object is a static large object manifest object.
    #: *Type: bool*
    is_static_large_object = resource.header("x-static-large-object",
                                             type=bool)
    #: If set, the value of the Content-Encoding metadata.
    #: If not set, this header is not returned by this operation.
    content_encoding = resource.header("content-encoding")
    #: If set, specifies the override behavior for the browser.
    #: For example, this header might specify that the browser use
    #: a download program to save this file rather than show the file,
    #: which is the default.
    #: If not set, this header is not returned by this operation.
    content_disposition = resource.header("content-disposition")
    #: Specifies the number of seconds after which the object is
    #: removed. Internally, the Object Storage system stores this
    #: value in the X-Delete-At metadata item.
    delete_after = resource.header("x-delete-after", type=int)
    #: If set, the time when the object will be deleted by the system
    #: in the format of a UNIX Epoch timestamp.
    #: If not set, this header is not returned by this operation.
    #: *Type: datetime object parsed from a UNIX epoch*
    delete_at = resource.header("x-delete-at", type=format.UNIXEpoch)
    #: If set, to this is a dynamic large object manifest object.
    #: The value is the container and object name prefix of the
    #: segment objects in the form container/prefix.
    object_manifest = resource.header("x-object-manifest")
    #: The timestamp of the transaction.
    #: *Type: datetime object parsed from a UNIX epoch*
    timestamp = resource.header("x-timestamp", type=format.UNIXEpoch)
    #: The date and time that the object was created or the last
    #: time that the metadata was changed.
    last_modified_at = resource.header("last_modified", alias="last-modified")

    # Headers for PUT and POST requests
    #: Set to chunked to enable chunked transfer encoding. If used,
    #: do not set the Content-Length header to a non-zero value.
    transfer_encoding = resource.header("transfer-encoding")
    #: If set to true, Object Storage guesses the content type based
    #: on the file extension and ignores the value sent in the
    #: Content-Type header, if present. *Type: bool*
    is_content_type_detected = resource.header("x-detect-content-type",
                                               type=bool)
    #: If set, this is the name of an object used to create the new
    #: object by copying the X-Copy-From object. The value is in form
    #: {container}/{object}. You must UTF-8-encode and then URL-encode
    #: the names of the container and object before you include them
    #: in the header.
    #: Using PUT with X-Copy-From has the same effect as using the
    #: COPY operation to copy an object.
    copy_from = resource.header("x-copy-from")

    # The Object Store treats the metadata for its resources inconsistently so
    # Object.set_metadata must override the BaseResource.set_metadata to
    # account for it.
    def set_metadata(self, session, metadata):
        # Filter out items with empty values so the create metadata behaviour
        # is the same as account and container
        filtered_metadata = \
            {key: value for key, value in metadata.iteritems() if value}

        # Get a copy of the original metadata so it doesn't get erased on POST
        # and update it with the new metadata values.
        obj = self.head(session)
        metadata2 = copy.deepcopy(obj.metadata)
        metadata2.update(filtered_metadata)

        # Include any original system metadata so it doesn't get erased on POST
        for key in self._system_metadata:
            value = getattr(obj, key)
            if value and key not in metadata2:
                metadata2[key] = value

        super(Object, self).set_metadata(session, metadata2)

    # The Object Store treats the metadata for its resources inconsistently so
    # Object.delete_metadata must override the BaseResource.delete_metadata to
    # account for it.
    def delete_metadata(self, session, keys):
        # Get a copy of the original metadata so it doesn't get erased on POST
        # and update it with the new metadata values.
        obj = self.head(session)
        metadata = copy.deepcopy(obj.metadata)

        # Include any original system metadata so it doesn't get erased on POST
        for key in self._system_metadata:
            value = getattr(obj, key)
            if value:
                metadata[key] = value

        # Remove the metadata
        for key in keys:
            if key == 'delete_after':
                del(metadata['delete_at'])
            else:
                del(metadata[key])

        url = self._get_url(self, self.id)
        session.post(url, endpoint_filter=self.service,
                     headers=self._calculate_headers(metadata))

    def get(self, session, include_headers=False, args=None):
        url = self._get_url(self, self.id)
        headers = {'Accept': 'bytes'}
        resp = session.get(url, endpoint_filter=self.service, headers=headers)
        resp = resp.content
        self._set_metadata()
        return resp

    def create(self, session):
        url = self._get_url(self, self.id)

        headers = self.get_headers()
        headers['Accept'] = ''
        if self.data is not None:
            resp = session.put(url, endpoint_filter=self.service,
                               data=self.data,
                               headers=headers).headers
        else:
            resp = session.post(url, endpoint_filter=self.service, data=None,
                                headers=headers).headers
        self.set_headers(resp)
        return self
