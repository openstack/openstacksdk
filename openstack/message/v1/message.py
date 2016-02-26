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

from six.moves.urllib import parse

from openstack.message import message_service
from openstack import resource


class Message(resource.Resource):
    resources_key = 'messages'
    base_path = "/queues/%(queue_name)s/messages"
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

    #: The name of the queue this Message belongs to.
    queue_name = None

    #: A relative href that references this Message.
    href = resource.prop("href")

    #: An arbitrary JSON document that constitutes the body of the message
    #: being sent.
    body = resource.prop("body")

    #: Specifies how long the server waits, in seconds, before marking the
    #: message as expired and removing it from the queue.
    ttl = resource.prop("ttl")

    #: Specifies how long the message has been in the queue, in seconds.
    age = resource.prop("age")

    @classmethod
    def create_messages(cls, session, messages):
        if len(messages) == 0:
            raise ValueError('messages cannot be empty')

        for i, message in enumerate(messages, -1):
            if message.queue_name != messages[i].queue_name:
                raise ValueError('All queues in messages must be equal')
            if message.client_id != messages[i].client_id:
                raise ValueError('All clients in messages must be equal')

        url = cls._get_url({'queue_name': messages[0].queue_name})
        headers = {'Client-ID': messages[0].client_id}

        resp = session.post(url, endpoint_filter=cls.service, headers=headers,
                            data=json.dumps(messages, cls=MessageEncoder))
        resp = resp.json()

        messages_created = []
        hrefs = resp['resources']

        for i, href in enumerate(hrefs):
            message = Message.existing(**messages[i])
            message.href = href
            messages_created.append(message)

        return messages_created

    @classmethod
    def _strip_version(cls, href):
        path = parse.urlparse(href).path

        if path.startswith('/v'):
            return href[href.find('/', 1):]
        else:
            return href

    @classmethod
    def delete_by_id(cls, session, message, path_args=None):
        url = cls._strip_version(message.href)
        headers = {
            'Client-ID': message.client_id,
            'Accept': '',
        }
        session.delete(url, endpoint_filter=cls.service, headers=headers)


class MessageEncoder(json.JSONEncoder):
    def default(self, message):
        return {'body': message.body, 'ttl': message.ttl}
