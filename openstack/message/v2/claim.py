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

from typing import Any, Self
import uuid

from keystoneauth1 import adapter

from openstack.message.v2 import _base
from openstack import resource


class Claim(_base.MessageResource):
    resources_key = 'claims'
    base_path = '/queues/%(queue_name)s/claims'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    commit_method = 'PATCH'

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

    def _translate_response(
        self,
        response: Any,
        has_body: bool | None = None,
        error_message: str | None = None,
        *,
        resource_response_key: str | None = None,
    ) -> None:
        # For case no message was claimed successfully, 204 No Content
        # message will be returned. In other cases, we translate response
        # body which has `messages` field(list) included.
        if response.status_code == 204:
            return

        super()._translate_response(
            response,
            has_body,
            error_message,
            resource_response_key=resource_response_key,
        )
        if has_body and self.location:
            # Extract claim ID from location
            self.id = self.location.split("claims/")[1]

    def create(
        self,
        session: adapter.Adapter,
        prepend_key: bool = False,
        base_path: str | None = None,
        *,
        resource_request_key: str | None = None,
        resource_response_key: str | None = None,
        microversion: str | None = None,
        **params: Any,
    ) -> Self:
        request = self._prepare_request(
            requires_id=False, prepend_key=prepend_key, base_path=base_path
        )
        headers: dict[str, str] = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id() or "",
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

    def commit(
        self,
        session: adapter.Adapter,
        prepend_key: bool = True,
        has_body: bool = True,
        retry_on_conflict: bool | None = None,
        base_path: str | None = None,
        **kwargs: Any,
    ) -> Self:
        request = self._prepare_request(
            prepend_key=prepend_key, base_path=base_path
        )
        headers: dict[str, str] = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id() or "",
        }

        request.headers.update(headers)
        session.patch(request.url, json=request.body, headers=request.headers)

        return self
