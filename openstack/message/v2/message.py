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

from openstack.message import message_service
from openstack import resource2


class Message(resource2.Resource):
    # FIXME(anyone): The name string of `location` field of Zaqar API response
    # is lower case. That is inconsistent with the guide from API-WG. This is
    # a workaround for this issue.
    location = resource2.Header("location")

    resources_key = 'messages'
    base_path = '/queues/%(queue_name)s/messages'
    service = message_service.MessageService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_get = True
    allow_delete = True

    _query_mapping = resource2.QueryParameters("echo", "include_claimed")

    # Properties
    #: The value in second to specify how long the message has been
    #: posted to the queue.
    age = resource2.Body("age")
    #: A dictionary specifies an arbitrary document that constitutes the
    #: body of the message being sent.
    body = resource2.Body("body")
    #: An uri string describe the location of the message resource.
    href = resource2.Body("href")
    #: The value in seconds to specify how long the server waits before
    #: marking the message as expired and removing it from the queue.
    ttl = resource2.Body("ttl")
    #: The name of target queue message is post to or got from.
    queue_name = resource2.URI("queue_name")
    #: The ID to identify the client accessing Zaqar API. Must be specified
    #: in header for each API request.
    client_id = resource2.Header("Client-ID")
    #: The ID to identify the project accessing Zaqar API. Must be specified
    #: in case keystone auth is not enabled in Zaqar service.
    project_id = resource2.Header("X-PROJECT-ID")

    def post(self, session, messages):
        request = self._prepare_request(requires_id=False, prepend_key=True)
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id()
        }
        request.headers.update(headers)
        request.body = {'messages': messages}
        response = session.post(request.uri, endpoint_filter=self.service,
                                json=request.body, headers=request.headers)

        return response.json()['resources']

    @classmethod
    def list(cls, session, paginated=True, **params):
        """This method is a generator which yields message objects.

        This is almost the copy of list method of resource2.Resource class.
        The only difference is the request header now includes `Client-ID`
        and `X-PROJECT-ID` fields which are required by Zaqar v2 API.
        """
        more_data = True
        uri = cls.base_path % params
        headers = {
            "Client-ID": params.get('client_id', None) or str(uuid.uuid4()),
            "X-PROJECT-ID": params.get('project_id', None
                                       ) or session.get_project_id()
        }

        query_params = cls._query_mapping._transpose(params)
        while more_data:
            resp = session.get(uri, endpoint_filter=cls.service,
                               headers=headers, params=query_params)
            resp = resp.json()
            resp = resp[cls.resources_key]

            if not resp:
                more_data = False

            yielded = 0
            new_marker = None
            for data in resp:
                value = cls.existing(**data)
                new_marker = value.id
                yielded += 1
                yield value

            if not paginated:
                return
            if "limit" in query_params and yielded < query_params["limit"]:
                return
            query_params["limit"] = yielded
            query_params["marker"] = new_marker

    def get(self, session, requires_id=True):
        request = self._prepare_request(requires_id=requires_id)
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id()
        }

        request.headers.update(headers)
        response = session.get(request.uri, endpoint_filter=self.service,
                               headers=headers)
        self._translate_response(response)

        return self

    def delete(self, session):
        request = self._prepare_request()
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id()
        }

        request.headers.update(headers)
        # For Zaqar v2 API requires client to specify claim_id as query
        # parameter when deleting a message that has been claimed, we
        # rebuild the request URI if claim_id is not None.
        if self.claim_id:
            request.uri += '?claim_id=%s' % self.claim_id
        response = session.delete(request.uri, endpoint_filter=self.service,
                                  headers=headers)

        self._translate_response(response, has_body=False)
        return self
