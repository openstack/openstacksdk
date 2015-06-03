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

from openstack.message.v1 import claim
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

    def create_messages(self, values):
        """Create new messages

        :param list values: The list of
                    :class:`~openstack.message.v1.message.Message`s to create.

        :returns: The results of message creation
        :rtype: list messages: The list of
                    :class:`~openstack.message.v1.message.Message`s created.
        """
        return message.Message.create_messages(self.session, values)

    def claim_messages(self, value):
        """Claims a set of messages.

        :param value: The value must be a
                      :class:`~openstack.message.v1.claim.Claim` instance.

        :returns: The results of a claim
        :rtype: list messages: The list of
                    :class:`~openstack.message.v1.message.Message`s claimed.
        """
        return claim.Claim.claim_messages(self.session, value)

    def delete_message(self, value):
        """Delete a message

        :param value: The value must be a
                      :class:`~openstack.message.v1.message.Message` instance.

        :returns: ``None``
        """
        message.Message.delete_by_id(self.session, value)
