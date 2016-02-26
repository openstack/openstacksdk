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

import json

from openstack import exceptions
from openstack.message import message_service
from openstack.message.v1 import message
from openstack import resource


class Claim(resource.Resource):
    resources_key = 'claims'
    base_path = "/queues/%(queue_name)s/claims"
    service = message_service.MessageService()

    # capabilities
    allow_create = True
    allow_list = False
    allow_retrieve = False
    allow_delete = False

    #: A ID for each client instance. The ID must be submitted in its
    #: canonical form (for example, 3381af92-2b9e-11e3-b191-71861300734c).
    #: The client generates this ID once. The client ID persists between
    #: restarts of the client so the client should reuse that same ID.
    #: All message-related operations require the use of the client ID in
    #: the headers to ensure that messages are not echoed back to the client
    #: that posted them, unless the client explicitly requests this.
    client_id = None

    #: The name of the queue this Claim belongs to.
    queue_name = None

    #: Specifies the number of Messages to return.
    limit = None

    #: Specifies how long the server waits before releasing the claim,
    #: in seconds.
    ttl = resource.prop("ttl")

    #: Specifies the message grace period, in seconds.
    grace = resource.prop("grace")

    @classmethod
    def claim_messages(cls, session, claim):
        """Create a remote resource from this instance."""
        url = cls._get_url({'queue_name': claim.queue_name})
        headers = {'Client-ID': claim.client_id}
        params = {'limit': claim.limit} if claim.limit else None
        body = []

        try:
            resp = session.post(url, endpoint_filter=cls.service,
                                headers=headers,
                                data=json.dumps(claim, cls=ClaimEncoder),
                                params=params)
            body = resp.json()
        except exceptions.InvalidResponse as e:
            # The Message Service will respond with a 204 and no content in
            # the body when there are no messages to claim. The transport
            # layer doesn't like that and we have to correct for it here.
            # Ultimately it's a bug in the v1.0 Message Service API.
            # TODO(etoews): API is fixed in v1.1 so fix this for message.v1_1
            # https://wiki.openstack.org/wiki/Zaqar/specs/api/v1.1
            if e.response.status_code != 204:
                raise e

        for message_attrs in body:
            yield message.Message.new(
                client_id=claim.client_id,
                queue_name=claim.queue_name,
                **message_attrs)


class ClaimEncoder(json.JSONEncoder):
    def default(self, claim):
        return {'ttl': claim.ttl, 'grace': claim.grace}
