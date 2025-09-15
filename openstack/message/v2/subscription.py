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


class Subscription(_base.MessageResource):
    resources_key = 'subscriptions'
    base_path = '/queues/%(queue_name)s/subscriptions'

    # capabilities
    allow_create = True
    allow_list = True
    allow_fetch = True
    allow_delete = True

    # Properties
    #: The value in seconds indicating how long the subscription has existed.
    age = resource.Body("age")
    #: Alternate id of the subscription. This key is used in response of
    #: subscription create API to return id of subscription created.
    subscription_id = resource.Body("subscription_id", alternate_id=True)
    #: The extra metadata for the subscription. The value must be a dict.
    #: If the subscriber is `mailto`. The options can contain `from` and
    #: `subject` to indicate the email's author and title.
    options = resource.Body("options", type=dict)
    #: The queue name which the subscription is registered on.
    source = resource.Body("source")
    #: The destination of the message. Two kinds of subscribers are supported:
    #: http/https and email. The http/https subscriber should start with
    #: `http/https`. The email subscriber should start with `mailto`.
    subscriber = resource.Body("subscriber")
    #: Number of seconds the subscription remains alive? The ttl value must
    #: be great than 60 seconds. The default value is 3600 seconds.
    ttl = resource.Body("ttl")
    #: The queue name which the subscription is registered on.
    queue_name = resource.URI("queue_name")

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

        self._translate_response(response)
        return self
