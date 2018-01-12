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

from openstack import exceptions
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
    pagination_key = 'X-Container-Object-Count'
    service = object_store_service.ObjectStoreService()

    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True
    allow_head = True

    # Data to be passed during a POST call to create an object on the server.
    # TODO(mordred) Make a base class BaseDataResource that can be used here
    # and with glance images that has standard overrides for dealing with
    # binary data.
    data = None

    # URL parameters
    #: The unique name for the container.
    container = resource.URI("container")
    #: The unique name for the object.
    name = resource.Body("name", alternate_id=True)

    # Object details
    # Make these private because they should only matter in the case where
    # we have a Body with no headers (like if someone programmatically is
    # creating an Object)
    _hash = resource.Body("hash")
    _bytes = resource.Body("bytes", type=int)
    _last_modified = resource.Body("last_modified")
    _content_type = resource.Body("content_type")

    # Headers for HEAD and GET requests
    #: If set to True, Object Storage queries all replicas to return
    #: the most recent one. If you omit this header, Object Storage
    #: responds faster after it finds one valid replica. Because
    #: setting this header to True is more expensive for the back end,
    #: use it only when it is absolutely needed. *Type: bool*
    is_newest = resource.Header("x-newest", type=bool)
    #: TODO(briancurtin) there's a lot of content here...
    range = resource.Header("range", type=dict)
    #: See http://www.ietf.org/rfc/rfc2616.txt.
    if_match = resource.Header("if-match", type=list)
    #: In combination with Expect: 100-Continue, specify an
    #: "If-None-Match: \*" header to query whether the server already
    #: has a copy of the object before any data is sent.
    if_none_match = resource.Header("if-none-match", type=list)
    #: See http://www.ietf.org/rfc/rfc2616.txt.
    if_modified_since = resource.Header("if-modified-since", type=str)
    #: See http://www.ietf.org/rfc/rfc2616.txt.
    if_unmodified_since = resource.Header("if-unmodified-since", type=str)

    # Query parameters
    #: Used with temporary URLs to sign the request. For more
    #: information about temporary URLs, see OpenStack Object Storage
    #: API v1 Reference.
    signature = resource.Header("signature")
    #: Used with temporary URLs to specify the expiry time of the
    #: signature. For more information about temporary URLs, see
    #: OpenStack Object Storage API v1 Reference.
    expires_at = resource.Header("expires")
    #: If you include the multipart-manifest=get query parameter and
    #: the object is a large object, the object contents are not
    #: returned. Instead, the manifest is returned in the
    #: X-Object-Manifest response header for dynamic large objects
    #: or in the response body for static large objects.
    multipart_manifest = resource.Header("multipart-manifest")

    # Response headers from HEAD and GET
    #: HEAD operations do not return content. However, in this
    #: operation the value in the Content-Length header is not the
    #: size of the response body. Instead it contains the size of
    #: the object, in bytes.
    content_length = resource.Header(
        "content-length", type=int, alias='_bytes')
    #: The MIME type of the object.
    content_type = resource.Header("content-type", alias="_content_type")
    #: The type of ranges that the object accepts.
    accept_ranges = resource.Header("accept-ranges")
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
    etag = resource.Header("etag", alias='_hash')
    #: Set to True if this object is a static large object manifest object.
    #: *Type: bool*
    is_static_large_object = resource.Header("x-static-large-object",
                                             type=bool)
    #: If set, the value of the Content-Encoding metadata.
    #: If not set, this header is not returned by this operation.
    content_encoding = resource.Header("content-encoding")
    #: If set, specifies the override behavior for the browser.
    #: For example, this header might specify that the browser use
    #: a download program to save this file rather than show the file,
    #: which is the default.
    #: If not set, this header is not returned by this operation.
    content_disposition = resource.Header("content-disposition")
    #: Specifies the number of seconds after which the object is
    #: removed. Internally, the Object Storage system stores this
    #: value in the X-Delete-At metadata item.
    delete_after = resource.Header("x-delete-after", type=int)
    #: If set, the time when the object will be deleted by the system
    #: in the format of a UNIX Epoch timestamp.
    #: If not set, this header is not returned by this operation.
    delete_at = resource.Header("x-delete-at")
    #: If set, to this is a dynamic large object manifest object.
    #: The value is the container and object name prefix of the
    #: segment objects in the form container/prefix.
    object_manifest = resource.Header("x-object-manifest")
    #: The timestamp of the transaction.
    timestamp = resource.Header("x-timestamp")
    #: The date and time that the object was created or the last
    #: time that the metadata was changed.
    last_modified_at = resource.Header("last-modified", alias='_last_modified')

    # Headers for PUT and POST requests
    #: Set to chunked to enable chunked transfer encoding. If used,
    #: do not set the Content-Length header to a non-zero value.
    transfer_encoding = resource.Header("transfer-encoding")
    #: If set to true, Object Storage guesses the content type based
    #: on the file extension and ignores the value sent in the
    #: Content-Type header, if present. *Type: bool*
    is_content_type_detected = resource.Header("x-detect-content-type",
                                               type=bool)
    #: If set, this is the name of an object used to create the new
    #: object by copying the X-Copy-From object. The value is in form
    #: {container}/{object}. You must UTF-8-encode and then URL-encode
    #: the names of the container and object before you include them
    #: in the header.
    #: Using PUT with X-Copy-From has the same effect as using the
    #: COPY operation to copy an object.
    copy_from = resource.Header("x-copy-from")

    has_body = False

    def __init__(self, data=None, **attrs):
        super(_base.BaseResource, self).__init__(**attrs)
        self.data = data

    # The Object Store treats the metadata for its resources inconsistently so
    # Object.set_metadata must override the BaseResource.set_metadata to
    # account for it.
    def set_metadata(self, session, metadata):
        # Filter out items with empty values so the create metadata behaviour
        # is the same as account and container
        filtered_metadata = \
            {key: value for key, value in metadata.items() if value}

        # Update from remote if we only have locally created information
        if not self.last_modified_at:
            self.head(session)

        # Get a copy of the original metadata so it doesn't get erased on POST
        # and update it with the new metadata values.
        metadata = copy.deepcopy(self.metadata)
        metadata.update(filtered_metadata)

        # Include any original system metadata so it doesn't get erased on POST
        for key in self._system_metadata:
            value = getattr(self, key)
            if value and key not in metadata:
                metadata[key] = value

        request = self._prepare_request()
        headers = self._calculate_headers(metadata)
        response = session.post(request.url, headers=headers)
        self._translate_response(response, has_body=False)
        self.metadata.update(metadata)

        return self

    # The Object Store treats the metadata for its resources inconsistently so
    # Object.delete_metadata must override the BaseResource.delete_metadata to
    # account for it.
    def delete_metadata(self, session, keys):
        if not keys:
            return
        # If we have an empty object, update it from the remote side so that
        # we have a copy of the original metadata. Deleting metadata requires
        # POSTing and overwriting all of the metadata. If we already have
        # metadata locally, assume this is an existing object.
        if not self.metadata:
            self.head(session)

        metadata = copy.deepcopy(self.metadata)

        # Include any original system metadata so it doesn't get erased on POST
        for key in self._system_metadata:
            value = getattr(self, key)
            if value:
                metadata[key] = value

        # Remove the requested metadata keys
        # TODO(mordred) Why don't we just look at self._header_mapping()
        # instead of having system_metadata?
        deleted = False
        attr_keys_to_delete = set()
        for key in keys:
            if key == 'delete_after':
                del(metadata['delete_at'])
            else:
                if key in metadata:
                    del(metadata[key])
                    # Delete the attribute from the local copy of the object.
                    # Metadata that doesn't have Component attributes is
                    # handled by self.metadata being reset when we run
                    # self.head
                    if hasattr(self, key):
                        attr_keys_to_delete.add(key)
                    deleted = True

        # Nothing to delete, skip the POST
        if not deleted:
            return self

        request = self._prepare_request()
        response = session.post(
            request.url, headers=self._calculate_headers(metadata))
        exceptions.raise_from_response(
            response, error_message="Error deleting metadata keys")

        # Only delete from local object if the remote delete was successful
        for key in attr_keys_to_delete:
            delattr(self, key)

        # Just update ourselves from remote again.
        return self.head(session)

    def _download(self, session, error_message=None, stream=False):
        request = self._prepare_request()
        request.headers['Accept'] = 'bytes'

        response = session.get(
            request.url, headers=request.headers, stream=stream)
        exceptions.raise_from_response(response, error_message=error_message)
        return response

    def download(self, session, error_message=None):
        response = self._download(session, error_message=error_message)
        return response.content

    def stream(self, session, error_message=None, chunk_size=1024):
        response = self._download(
            session, error_message=error_message, stream=True)
        return response.iter_content(chunk_size, decode_unicode=False)

    def create(self, session):
        request = self._prepare_request()
        request.headers['Accept'] = ''

        response = session.put(
            request.url,
            data=self.data,
            headers=request.headers)
        self._translate_response(response, has_body=False)
        return self
