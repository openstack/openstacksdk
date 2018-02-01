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
from openstack import resource


class Claim(resource.Resource):
    # FIXME(anyone): The name string of `location` field of Zaqar API response
    # is lower case. That is inconsistent with the guide from API-WG. This is
    # a workaround for this issue.
    location = resource.Header("location")

    resources_key = 'claims'
    base_path = '/queues/%(queue_name)s/claims'
    service = message_service.MessageService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    update_method = 'PATCH'

    # Properties
    #: The value in seconds indicating how long the claim has existed.
    age = resource.Body("age")
    #: In case worker stops responding for a long time, the server will
    #: extend the lifetime of claimed messages to be at least as long as
    #: the lifetime of the claim itself, plus the specified grace period.
    #: Must between 60 and 43200 seconds(12 hours).
    grace = resource.Body("grace")
    #: The number of messages to claim. Default 10, up to 20.
    limit = resource.Body("limit")
    #: Messages have been successfully claimed.
    messages = resource.Body("messages")
    #: Number of seconds the server wait before releasing the claim. Must
    #: between 60 and 43200 seconds(12 hours).
    ttl = resource.Body("ttl")
    #: The name of queue to claim message from.
    queue_name = resource.URI("queue_name")
    #: The ID to identify the client accessing Zaqar API. Must be specified
    #: in header for each API request.
    client_id = resource.Header("Client-ID")
    #: The ID to identify the project. Must be provided when keystone
    #: authentication is not enabled in Zaqar service.
    project_id = resource.Header("X-PROJECT-ID")

    def _translate_response(self, response, has_body=True):
        super(Claim, self)._translate_response(response, has_body=has_body)
        if has_body and self.location:
            # Extract claim ID from location
            self.id = self.location.split("claims/")[1]

    def create(self, session, prepend_key=False):
        request = self._prepare_request(requires_id=False,
                                        prepend_key=prepend_key)
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id()
        }
        request.headers.update(headers)
        response = session.post(request.url,
                                json=request.body, headers=request.headers)

        # For case no message was claimed successfully, 204 No Content
        # message will be returned. In other cases, we translate response
        # body which has `messages` field(list) included.
        if response.status_code != 204:
            self._translate_response(response)

        return self

    def get(self, session, requires_id=True, error_message=None):
        request = self._prepare_request(requires_id=requires_id)
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id()
        }

        request.headers.update(headers)
        response = session.get(request.url,
                               headers=request.headers)
        self._translate_response(response)

        return self

    def update(self, session, prepend_key=False, has_body=False):
        request = self._prepare_request(prepend_key=prepend_key)
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id()
        }

        request.headers.update(headers)
        session.patch(request.url,
                      json=request.body, headers=request.headers)

        return self

    def delete(self, session):
        request = self._prepare_request()
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id()
        }

        request.headers.update(headers)
        response = session.delete(request.url,
                                  headers=request.headers)

        self._translate_response(response, has_body=False)
        return self
