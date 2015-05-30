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

from openstack.message.v1 import message
from openstack.message.v1 import queue
from openstack import proxy


class Proxy(proxy.BaseProxy):

    def create_queue(self, **attrs):
        """Create a new queue from attributes

        :param dict attrs: Keyword arguments which will be used to create
                           a :class:`~openstack.message.v1.queue.Queue`,
                           comprised of the properties on the Queue class.

        :returns: The results of queue creation
        :rtype: :class:`~openstack.message.v1.queue.Queue`
        """
        return self._create(queue.Queue, **attrs)

    def delete_queue(self, value, ignore_missing=True):
        """Delete a queue

        :param value: The value can be either the name of a queue or a
                      :class:`~openstack.message.v1.queue.Queue` instance.
        :param bool ignore_missing: When set to ``False``
                    :class:`~openstack.exceptions.ResourceNotFound` will be
                    raised when the queue does not exist.
                    When set to ``True``, no exception will be set when
                    attempting to delete a nonexistent queue.

        :returns: ``None``
        """
        return self._delete(queue.Queue, value, ignore_missing=ignore_missing)

    def create_messages(self, client, value, messages):
        """Create new messages

        :param uuid client: A UUID for each client instance. The UUID must
                            be submitted in its canonical form (for
                            example, 3381af92-2b9e-11e3-b191-71861300734c).
                            The client generates this UUID once.
                            The client UUID persists between restarts of the
                            client so the client should reuse that same
                            UUID. All message-related operations
                            require the use of the client UUID in the headers
                            to ensure that messages are not echoed back
                            to the client that posted them, unless the
                            client explicitly requests this.
        :param value: The value can be either the name of a queue or a
                      :class:`~openstack.message.v1.queue.Queue` instance.
        :param list messages: The list of
                    :class:`~openstack.message.v1.message.Message`s to create.

        :returns: The results of message creation
        :rtype: list ids: A list of ids that correspond to the messages
                          created, in order.
        """
        queue_name = queue.Queue.get_id(value)
        return message.Message.create_from_messages(self.session, client,
                                                    queue_name, messages)
