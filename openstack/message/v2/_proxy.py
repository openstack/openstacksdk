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

import typing as ty

from openstack.message.v2 import claim as _claim
from openstack.message.v2 import message as _message
from openstack.message.v2 import queue as _queue
from openstack.message.v2 import subscription as _subscription
from openstack import proxy
from openstack import resource


class Proxy(proxy.Proxy):
    _resource_registry = {
        "claim": _claim.Claim,
        "message": _message.Message,
        "queue": _queue.Queue,
        "subscription": _subscription.Subscription,
    }

    def create_queue(self, **attrs):
        """Create a new queue from attributes

        :param dict attrs: Keyword arguments which will be used to create
            a :class:`~openstack.message.v2.queue.Queue`,
            comprised of the properties on the Queue class.

        :returns: The results of queue creation
        :rtype: :class:`~openstack.message.v2.queue.Queue`
        """
        return self._create(_queue.Queue, **attrs)

    def get_queue(self, queue):
        """Get a queue

        :param queue: The value can be the name of a queue or a
            :class:`~openstack.message.v2.queue.Queue` instance.

        :returns: One :class:`~openstack.message.v2.queue.Queue`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            queue matching the name could be found.
        """
        return self._get(_queue.Queue, queue)

    def queues(self, **query):
        """Retrieve a generator of queues

        :param kwargs query: Optional query parameters to be sent to
            restrict the queues to be returned. Available parameters include:

            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen queue. Use the limit
                parameter to make an initial limited request and use the ID of
                the last-seen queue from the response as the marker parameter
                value in a subsequent limited request.

        :returns: A generator of queue instances.
        """
        return self._list(_queue.Queue, **query)

    def delete_queue(self, value, ignore_missing=True):
        """Delete a queue

        :param value: The value can be either the name of a queue or a
            :class:`~openstack.message.v2.queue.Queue` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the queue does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent queue.

        :returns: ``None``
        """
        return self._delete(_queue.Queue, value, ignore_missing=ignore_missing)

    def post_message(self, queue_name, messages):
        """Post messages to given queue

        :param queue_name: The name of target queue to post message to.
        :param messages: List of messages body and TTL to post.
            :type messages: :py:class:`list`

        :returns: A string includes location of messages successfully posted.
        """
        message = self._get_resource(
            _message.Message, None, queue_name=queue_name
        )
        return message.post(self, messages)

    def messages(self, queue_name, **query):
        """Retrieve a generator of messages

        :param queue_name: The name of target queue to query messages from.
        :param kwargs query: Optional query parameters to be sent to
            restrict the messages to be returned. Available parameters include:

            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen subscription. Use the
                limit parameter to make an initial limited request and use the
                ID of the last-seen subscription from the response as the
                marker parameter value in a subsequent limited request.
            * echo: Indicate if the messages can be echoed back to the client
                that posted them.
            * include_claimed: Indicate if the messages list should include
                the claimed messages.

        :returns: A generator of message instances.
        """
        query["queue_name"] = queue_name
        return self._list(_message.Message, **query)

    def get_message(self, queue_name, message):
        """Get a message

        :param queue_name: The name of target queue to get message from.
        :param message: The value can be the name of a message or a
            :class:`~openstack.message.v2.message.Message` instance.

        :returns: One :class:`~openstack.message.v2.message.Message`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            message matching the criteria could be found.
        """
        message = self._get_resource(
            _message.Message, message, queue_name=queue_name
        )
        return self._get(_message.Message, message)

    def delete_message(
        self, queue_name, value, claim=None, ignore_missing=True
    ):
        """Delete a message

        :param queue_name: The name of target queue to delete message from.
        :param value: The value can be either the name of a message or a
            :class:`~openstack.message.v2.message.Message` instance.
        :param claim: The value can be the ID or a
            :class:`~openstack.message.v2.claim.Claim` instance of
            the claim seizing the message. If None, the message has
            not been claimed.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the message does not exist.
            When set to ``True``, no exception will be set when
            attempting to delete a nonexistent message.

        :returns: ``None``
        """
        message = self._get_resource(
            _message.Message, value, queue_name=queue_name
        )
        message.claim_id = resource.Resource._get_id(claim)
        return self._delete(
            _message.Message, message, ignore_missing=ignore_missing
        )

    def create_subscription(self, queue_name, **attrs):
        """Create a new subscription from attributes

        :param queue_name: The name of target queue to subscribe on.
        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.message.v2.subscription.Subscription`,
            comprised of the properties on the Subscription class.

        :returns: The results of subscription creation
        :rtype: :class:`~openstack.message.v2.subscription.Subscription`
        """
        return self._create(
            _subscription.Subscription, queue_name=queue_name, **attrs
        )

    def subscriptions(self, queue_name, **query):
        """Retrieve a generator of subscriptions

        :param queue_name: The name of target queue to subscribe on.
        :param kwargs query: Optional query parameters to be sent to
            restrict the subscriptions to be returned. Available parameters
            include:

            * limit: Requests at most the specified number of items be
                returned from the query.
            * marker: Specifies the ID of the last-seen subscription. Use the
                limit parameter to make an initial limited request and use the
                ID of the last-seen subscription from the response as the
                marker parameter value in a subsequent limited request.

        :returns: A generator of subscription instances.
        """
        query["queue_name"] = queue_name
        return self._list(_subscription.Subscription, **query)

    def get_subscription(self, queue_name, subscription):
        """Get a subscription

        :param queue_name: The name of target queue of subscription.
        :param message: The value can be the ID of a subscription or a
            :class:`~openstack.message.v2.subscription.Subscription` instance.

        :returns: One :class:`~openstack.message.v2.subscription.Subscription`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            subscription matching the criteria could be found.
        """
        subscription = self._get_resource(
            _subscription.Subscription, subscription, queue_name=queue_name
        )
        return self._get(_subscription.Subscription, subscription)

    def delete_subscription(self, queue_name, value, ignore_missing=True):
        """Delete a subscription

        :param queue_name: The name of target queue to delete subscription
            from.
        :param value: The value can be either the name of a subscription or a
            :class:`~openstack.message.v2.subscription.Subscription`
            instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the subscription does not exist.
            When set to ``True``, no exception will be thrown when
            attempting to delete a nonexistent subscription.

        :returns: ``None``
        """
        subscription = self._get_resource(
            _subscription.Subscription, value, queue_name=queue_name
        )
        return self._delete(
            _subscription.Subscription,
            subscription,
            ignore_missing=ignore_missing,
        )

    def create_claim(self, queue_name, **attrs):
        """Create a new claim from attributes

        :param queue_name: The name of target queue to claim message from.
        :param dict attrs: Keyword arguments which will be used to create a
            :class:`~openstack.message.v2.claim.Claim`,
            comprised of the properties on the Claim class.

        :returns: The results of claim creation
        :rtype: :class:`~openstack.message.v2.claim.Claim`
        """
        return self._create(_claim.Claim, queue_name=queue_name, **attrs)

    def get_claim(self, queue_name, claim):
        """Get a claim

        :param queue_name: The name of target queue to claim message from.
        :param claim: The value can be either the ID of a claim or a
            :class:`~openstack.message.v2.claim.Claim` instance.

        :returns: One :class:`~openstack.message.v2.claim.Claim`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            claim matching the criteria could be found.
        """
        return self._get(_claim.Claim, claim, queue_name=queue_name)

    def update_claim(self, queue_name, claim, **attrs):
        """Update an existing claim from attributes

        :param queue_name: The name of target queue to claim message from.
        :param claim: The value can be either the ID of a claim or a
            :class:`~openstack.message.v2.claim.Claim` instance.
        :param dict attrs: Keyword arguments which will be used to update a
            :class:`~openstack.message.v2.claim.Claim`,
            comprised of the properties on the Claim class.

        :returns: The results of claim update
        :rtype: :class:`~openstack.message.v2.claim.Claim`
        """
        return self._update(
            _claim.Claim, claim, queue_name=queue_name, **attrs
        )

    def delete_claim(self, queue_name, claim, ignore_missing=True):
        """Delete a claim

        :param queue_name: The name of target queue to claim messages from.
        :param claim: The value can be either the ID of a claim or a
            :class:`~openstack.message.v2.claim.Claim` instance.
        :param bool ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be
            raised when the claim does not exist.
            When set to ``True``, no exception will be thrown when
            attempting to delete a nonexistent claim.

        :returns: ``None``
        """
        return self._delete(
            _claim.Claim,
            claim,
            queue_name=queue_name,
            ignore_missing=ignore_missing,
        )

    # ========== Utilities ==========

    def wait_for_status(
        self,
        res: resource.ResourceT,
        status: str,
        failures: ty.Optional[list[str]] = None,
        interval: ty.Union[int, float, None] = 2,
        wait: ty.Optional[int] = None,
        attribute: str = 'status',
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for the resource to be in a particular status.

        :param session: The session to use for making this request.
        :param resource: The resource to wait on to reach the status. The
            resource must have a status attribute specified via ``attribute``.
        :param status: Desired status of the resource.
        :param failures: Statuses that would indicate the transition
            failed such as 'ERROR'. Defaults to ['ERROR'].
        :param interval: Number of seconds to wait between checks.
        :param wait: Maximum number of seconds to wait for transition.
            Set to ``None`` to wait forever.
        :param attribute: Name of the resource attribute that contains the
            status.
        :param callback: A callback function. This will be called with a single
            value, progress. This is API specific but is generally a percentage
            value from 0-100.

        :return: The updated resource.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if the
            transition to status failed to occur in ``wait`` seconds.
        :raises: :class:`~openstack.exceptions.ResourceFailure` if the resource
            transitioned to one of the states in ``failures``.
        :raises: :class:`~AttributeError` if the resource does not have a
            ``status`` attribute
        """
        return resource.wait_for_status(
            self, res, status, failures, interval, wait, attribute, callback
        )

    def wait_for_delete(
        self,
        res: resource.ResourceT,
        interval: int = 2,
        wait: int = 120,
        callback: ty.Optional[ty.Callable[[int], None]] = None,
    ) -> resource.ResourceT:
        """Wait for a resource to be deleted.

        :param res: The resource to wait on to be deleted.
        :param interval: Number of seconds to wait before to consecutive
            checks.
        :param wait: Maximum number of seconds to wait before the change.
        :param callback: A callback function. This will be called with a single
            value, progress, which is a percentage value from 0-100.

        :returns: The resource is returned on success.
        :raises: :class:`~openstack.exceptions.ResourceTimeout` if transition
            to delete failed to occur in the specified seconds.
        """
        return resource.wait_for_delete(self, res, interval, wait, callback)
