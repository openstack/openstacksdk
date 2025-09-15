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


class Queue(_base.MessageResource):
    resources_key = "queues"
    base_path = "/queues"

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    # Properties
    #: The default TTL of messages defined for a queue, which will effect for
    #: any messages posted to the queue.
    default_message_ttl = resource.Body("_default_message_ttl")
    #: Description of the queue.
    description = resource.Body("description")
    #: The max post size of messages defined for a queue, which will effect
    #: for any messages posted to the queue.
    max_messages_post_size = resource.Body("_max_messages_post_size")
    #: Name of the queue. The name is the unique identity of a queue. It
    #: must not exceed 64 bytes in length, and it is limited to US-ASCII
    #: letters, digits, underscores, and hyphens.
    name = resource.Body("name", alternate_id=True)

    def create(self, session, prepend_key=False, base_path=None, **kwargs):
        request = self._prepare_request(
            requires_id=True, prepend_key=prepend_key, base_path=None
        )
        headers = {
            "Client-ID": self.client_id or str(uuid.uuid4()),
            "X-PROJECT-ID": self.project_id or session.get_project_id(),
        }
        request.headers.update(headers)
        response = session.put(
            request.url, json=request.body, headers=request.headers
        )

        self._translate_response(response, has_body=False)
        return self
