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

from openstack.message import message_service
from openstack import resource

from six.moves.urllib import parse


class Message(resource.Resource):
    resources_key = 'messages'
    base_path = "/queues/%(queue_name)s/messages"
    service = message_service.MessageService()

    # capabilities
    allow_create = True
    allow_list = False
    allow_retrieve = False
    allow_delete = False

    #: An arbitrary JSON document that constitutes the body of the message
    #: being sent.
    body = resource.prop("body")

    #: Specifies how long the server waits, in seconds, before marking the
    #: message as expired and removing it from the queue.
    ttl = resource.prop("ttl")

    #: Specifies how long the message has been in the queue, in seconds.
    age = resource.prop("age")

    @staticmethod
    def get_message_id(href):
        """Get the ID of a message, which is the last component in an href."""
        path = parse.urlparse(href).path
        return path[path.rfind('/')+1:]

    @classmethod
    def create_from_messages(cls, session, client_id=None, queue_name=None,
                             messages=None):
        """Create a remote resource from this instance."""
        url = cls._get_url({'queue_name': queue_name})
        headers = {'Client-ID': client_id}

        resp = session.post(url, service=cls.service, headers=headers,
                            data=json.dumps(messages, cls=MessageEncoder))

        hrefs = resp.body['resources']
        ids = [cls.get_message_id(href) for href in hrefs]

        return ids


class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj._attrs
