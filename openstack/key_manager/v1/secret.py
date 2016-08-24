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

from openstack.key_manager import key_manager_service
from openstack.key_manager.v1 import _format
from openstack import resource2
from openstack import utils


class Secret(resource2.Resource):
    resources_key = 'secrets'
    base_path = '/secrets'
    service = key_manager_service.KeyManagerService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource2.QueryParameters("name", "mode", "bits",
                                               "secret_type", "acl_only",
                                               "created", "updated",
                                               "expiration", "sort",
                                               algorithm="alg")

    # Properties
    #: Metadata provided by a user or system for informational purposes
    algorithm = resource2.Body('algorithm')
    #: Metadata provided by a user or system for informational purposes.
    #: Value must be greater than zero.
    bit_length = resource2.Body('bit_length')
    #: A list of content types
    content_types = resource2.Body('content_types', type=dict)
    #: Once this timestamp has past, the secret will no longer be available.
    expires_at = resource2.Body('expiration')
    #: Timestamp of when the secret was created.
    created_at = resource2.Body('created')
    #: Timestamp of when the secret was last updated.
    updated_at = resource2.Body('updated')
    #: The type/mode of the algorithm associated with the secret information.
    mode = resource2.Body('mode')
    #: The name of the secret set by the user
    name = resource2.Body('name')
    #: A URI to the sercret
    secret_ref = resource2.Body('secret_ref')
    #: The ID of the secret
    # NOTE: This is not really how alternate IDs are supposed to work and
    # ultimately means this has to work differently than all other services
    # in all of OpenStack because of the departure from using actual IDs
    # that even this service can't even use itself.
    secret_id = resource2.Body('secret_ref', alternate_id=True,
                               type=_format.HREFToUUID)
    #: Used to indicate the type of secret being stored.
    secret_type = resource2.Body('secret_type')
    #: The status of this secret
    status = resource2.Body('status')
    #: A timestamp when this secret was updated.
    updated_at = resource2.Body('updated')
    #: The secret's data to be stored. payload_content_type must also
    #: be supplied if payload is included. (optional)
    payload = resource2.Body('payload')
    #: The media type for the content of the payload.
    #: (required if payload is included)
    payload_content_type = resource2.Body('payload_content_type')
    #: The encoding used for the payload to be able to include it in
    #: the JSON request. Currently only base64 is supported.
    #: (required if payload is encoded)
    payload_content_encoding = resource2.Body('payload_content_encoding')

    def get(self, session, requires_id=True):
        request = self._prepare_request(requires_id=requires_id)

        response = session.get(request.uri,
                               endpoint_filter=self.service).json()

        content_type = None
        if self.payload_content_type is not None:
            content_type = self.payload_content_type
        elif "content_types" in response:
            content_type = response["content_types"]["default"]

        # Only try to get the payload if a content type has been explicitly
        # specified or if one was found in the metadata response
        if content_type is not None:
            payload = session.get(utils.urljoin(request.uri, "payload"),
                                  endpoint_filter=self.service,
                                  headers={"Accept": content_type})
            response["payload"] = payload.text

        # We already have the JSON here so don't call into _translate_response
        body = self._filter_component(response, self._body_mapping())
        self._body.attributes.update(body)
        self._body.clean()

        return self
