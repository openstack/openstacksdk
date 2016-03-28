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

from openstack import format
from openstack.object_store.v1 import _base
from openstack import resource


class Container(_base.BaseResource):
    _custom_metadata_prefix = "X-Container-Meta-"
    _system_metadata = {
        "content_type": "content-type",
        "is_content_type_detected": "x-detect-content-type",
        "versions_location": "x-versions-location",
        "read_ACL": "x-container-read",
        "write_ACL": "x-container-write",
        "sync_to": "x-container-sync-to",
        "sync_key": "x-container-sync-key"
    }

    base_path = "/"
    id_attribute = "name"

    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    allow_head = True

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
    object_count = resource.header("x-container-object-count", type=int)
    #: The count of bytes used in total.
    bytes_used = resource.header("x-container-bytes-used", type=int)
    #: The timestamp of the transaction.
    #: *Type: datetime object parsed from a UNIX epoch*
    timestamp = resource.header("x-timestamp", type=format.UNIXEpoch)

    # Request headers (when id=None)
    #: If set to True, Object Storage queries all replicas to return the
    #: most recent one. If you omit this header, Object Storage responds
    #: faster after it finds one valid replica. Because setting this
    #: header to True is more expensive for the back end, use it only
    #: when it is absolutely needed. *Type: bool*
    is_newest = resource.header("x-newest", type=bool)

    # Request headers (when id=name)
    #: The ACL that grants read access. If not set, this header is not
    #: returned by this operation.
    read_ACL = resource.header("x-container-read")
    #: The ACL that grants write access. If not set, this header is not
    #: returned by this operation.
    write_ACL = resource.header("x-container-write")
    #: The destination for container synchronization. If not set,
    #: this header is not returned by this operation.
    sync_to = resource.header("x-container-sync-to")
    #: The secret key for container synchronization. If not set,
    #: this header is not returned by this operation.
    sync_key = resource.header("x-container-sync-key")
    #: Enables versioning on this container. The value is the name
    #: of another container. You must UTF-8-encode and then URL-encode
    #: the name before you include it in the header. To disable
    #: versioning, set the header to an empty string.
    versions_location = resource.header("x-versions-location")
    #: The MIME type of the list of names.
    content_type = resource.header("content-type")
    #: If set to true, Object Storage guesses the content type based
    #: on the file extension and ignores the value sent in the
    #: Content-Type header, if present. *Type: bool*
    is_content_type_detected = resource.header("x-detect-content-type",
                                               type=bool)
    #: In combination with Expect: 100-Continue, specify an
    #: "If-None-Match: \*" header to query whether the server already
    #: has a copy of the object before any data is sent.
    if_none_match = resource.header("if-none-match")

    @classmethod
    def create_by_id(cls, session, attrs, resource_id=None):
        """Create a Resource from its attributes.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`
        :param dict attrs: The attributes to be sent in the body
                           of the request.
        :param resource_id: This resource's identifier, if needed by
                            the request. The default is ``None``.

        :return: A ``dict`` representing the response headers.
        """
        url = cls._get_url(None, resource_id)
        headers = attrs.get(resource.HEADERS, dict())
        headers['Accept'] = ''
        return session.put(url, endpoint_filter=cls.service,
                           headers=headers).headers

    def create(self, session):
        """Create a Resource from this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~openstack.session.Session`

        :return: This instance.
        """
        resp = self.create_by_id(session, self._attrs, self.id)
        self.set_headers(resp)
        self._reset_dirty()
        return self
