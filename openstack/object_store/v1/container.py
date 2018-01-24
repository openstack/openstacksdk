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
    pagination_key = 'X-Account-Container-Count'

    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True
    allow_head = True

    # Container body data (when id=None)
    #: The name of the container.
    name = resource.Body("name", alternate_id=True, alias='id')
    #: The number of objects in the container.
    count = resource.Body("count", type=int, alias='object_count')
    #: The total number of bytes that are stored in Object Storage
    #: for the container.
    bytes = resource.Body("bytes", type=int, alias='bytes_used')

    # Container metadata (when id=name)
    #: The number of objects.
    object_count = resource.Header(
        "x-container-object-count", type=int, alias='count')
    #: The count of bytes used in total.
    bytes_used = resource.Header(
        "x-container-bytes-used", type=int, alias='bytes')
    #: The timestamp of the transaction.
    timestamp = resource.Header("x-timestamp")

    # Request headers (when id=None)
    #: If set to True, Object Storage queries all replicas to return the
    #: most recent one. If you omit this header, Object Storage responds
    #: faster after it finds one valid replica. Because setting this
    #: header to True is more expensive for the back end, use it only
    #: when it is absolutely needed. *Type: bool*
    is_newest = resource.Header("x-newest", type=bool)

    # Request headers (when id=name)
    #: The ACL that grants read access. If not set, this header is not
    #: returned by this operation.
    read_ACL = resource.Header("x-container-read")
    #: The ACL that grants write access. If not set, this header is not
    #: returned by this operation.
    write_ACL = resource.Header("x-container-write")
    #: The destination for container synchronization. If not set,
    #: this header is not returned by this operation.
    sync_to = resource.Header("x-container-sync-to")
    #: The secret key for container synchronization. If not set,
    #: this header is not returned by this operation.
    sync_key = resource.Header("x-container-sync-key")
    #: Enables versioning on this container. The value is the name
    #: of another container. You must UTF-8-encode and then URL-encode
    #: the name before you include it in the header. To disable
    #: versioning, set the header to an empty string.
    versions_location = resource.Header("x-versions-location")
    #: The MIME type of the list of names.
    content_type = resource.Header("content-type")
    #: If set to true, Object Storage guesses the content type based
    #: on the file extension and ignores the value sent in the
    #: Content-Type header, if present. *Type: bool*
    is_content_type_detected = resource.Header("x-detect-content-type",
                                               type=bool)
    # TODO(mordred) Shouldn't if-none-match be handled more systemically?
    #: In combination with Expect: 100-Continue, specify an
    #: "If-None-Match: \*" header to query whether the server already
    #: has a copy of the object before any data is sent.
    if_none_match = resource.Header("if-none-match")

    @classmethod
    def new(cls, **kwargs):
        # Container uses name as id. Proxy._get_resource calls
        # Resource.new(id=name) but then we need to do container.name
        # It's the same thing for Container - make it be the same.
        name = kwargs.pop('id', None)
        if name:
            kwargs.setdefault('name', name)
        return Container(_synchronized=True, **kwargs)

    def create(self, session, prepend_key=True):
        """Create a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param prepend_key: A boolean indicating whether the resource_key
                            should be prepended in a resource creation
                            request. Default to True.

        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_create` is not set to ``True``.
        """
        request = self._prepare_request(
            requires_id=True, prepend_key=prepend_key)
        response = session.put(
            request.url, json=request.body, headers=request.headers)

        self._translate_response(response, has_body=False)
        return self
