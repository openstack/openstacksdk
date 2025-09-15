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

import uuid

from openstack.message.v2 import _base
from openstack import resource


class Message(_base.MessageResource):
    resources_key = 'messages'
    base_path = '/queues/%(queue_name)s/messages'

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    _query_mapping = resource.QueryParameters("echo", "include_claimed")

    # Properties
    #: The value in second to specify how long the message has been
    #: posted to the queue.
    age = resource.Body("age")
    #: A dictionary specifies an arbitrary document that constitutes the
    #: body of the message being sent.
    body = resource.Body("body")
    #: An uri string describe the location of the message resource.
    href = resource.Body("href")
    #: The value in seconds to specify how long the server waits before
    #: marking the message as expired and removing it from the queue.
    ttl = resource.Body("ttl")
    #: The name of target queue message is post to or got from.
    queue_name = resource.URI("queue_name")

    # FIXME(stephenfin): This is actually a query arg but we need it for
    # deletions and resource.delete doesn't respect these currently
    claim_id: str | None = None

    def post(self, session, messages):
        request = self._prepare_request(requires_id=False, prepend_key=True)
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id(),
        }
        request.headers.update(headers)
        request.body = {'messages': messages}
        response = session.post(
            request.url, json=request.body, headers=request.headers
        )

        return response.json()['resources']

    def create(self, session, prepend_key=False, base_path=None, **kwargs):
        request = self._prepare_request(
            requires_id=False, prepend_key=prepend_key, base_path=base_path
        )
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id(),
        }
        request.headers.update(headers)
        response = session.post(
            request.url, json=request.body, headers=request.headers
        )

        # For case no message was claimed successfully, 204 No Content
        # message will be returned. In other cases, we translate response
        # body which has `messages` field(list) included.
        if response.status_code != 204:
            self._translate_response(response)

        return self

    def delete(
        self, session, error_message=None, *, microversion=None, **kwargs
    ):
        request = self._prepare_request()
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id(),
        }

        request.headers.update(headers)
        # For Zaqar v2 API requires client to specify claim_id as query
        # parameter when deleting a message that has been claimed, we
        # rebuild the request URI if claim_id is not None.
        if self.claim_id:
            request.url += f'?claim_id={self.claim_id}'
        response = session.delete(request.url, headers=headers)

        self._translate_response(response, has_body=False)
        return self
