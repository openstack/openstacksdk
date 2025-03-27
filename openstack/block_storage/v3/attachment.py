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

import os

from openstack import exceptions
from openstack import resource
from openstack import utils


class Attachment(resource.Resource):
    resource_key = "attachment"
    resources_key = "attachments"
    base_path = "/attachments"

    # capabilities
    allow_create = True
    allow_delete = True
    allow_commit = True
    allow_list = True
    allow_fetch = True

    _max_microversion = "3.54"

    # Properties
    #: The ID of the attachment.
    id = resource.Body("id")
    #: The status of the attachment.
    status = resource.Body("status")
    #: The UUID of the attaching instance.
    instance = resource.Body("instance")
    #: The UUID of the volume which the attachment belongs to.
    volume_id = resource.Body("volume_id")
    #: The time when attachment is attached.
    attached_at = resource.Body("attach_time")
    #: The time when attachment is detached.
    detached_at = resource.Body("detach_time")
    #: The attach mode of attachment, read-only ('ro') or read-and-write
    # ('rw'), default is 'rw'.
    attach_mode = resource.Body("mode")
    #: The connection info used for server to connect the volume.
    connection_info = resource.Body("connection_info")
    #: The connector object.
    connector = resource.Body("connector")

    def create(
        self,
        session,
        prepend_key=True,
        base_path=None,
        *,
        resource_request_key=None,
        resource_response_key=None,
        microversion=None,
        **params,
    ):
        if utils.supports_microversion(session, '3.54'):
            if not self.attach_mode:
                self._body.clean(only={'mode'})
        return super().create(
            session,
            prepend_key=prepend_key,
            base_path=base_path,
            resource_request_key=resource_request_key,
            resource_response_key=resource_response_key,
            microversion=microversion,
            **params,
        )

    def complete(self, session, *, microversion=None):
        """Mark the attachment as completed."""
        body = {'os-complete': self.id}
        if not microversion:
            microversion = self._get_microversion(session)
        url = os.path.join(Attachment.base_path, self.id, 'action')
        response = session.post(url, json=body, microversion=microversion)
        exceptions.raise_from_response(response)

    def _prepare_request_body(
        self,
        patch,
        prepend_key,
        *,
        resource_request_key=None,
    ):
        body = self._body.dirty
        if body.get('volume_id'):
            body['volume_uuid'] = body.pop('volume_id')
        if body.get('instance'):
            body['instance_uuid'] = body.pop('instance')
        if prepend_key and self.resource_key is not None:
            body = {self.resource_key: body}
        return body
