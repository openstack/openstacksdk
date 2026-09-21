Using OpenStack Message
=======================

Before working with the Message service, you'll need to create a connection
to your OpenStack cloud by following the :doc:`connect` user guide. This will
provide you with the ``conn`` variable used in the examples below.

.. contents:: Table of Contents
   :local:

The Message service provides message queues, along with the messages,
subscriptions and claims associated with them. The examples below show a
representative subset of what is possible; for the complete set of operations,
see the :doc:`Message proxy reference </user/proxies/message_v2>`.

Working with Queues
-------------------

To list the existing queues, use the
:meth:`~openstack.message.v2._proxy.Proxy.queues` method, which returns a
generator of :class:`~openstack.message.v2.queue.Queue` objects. Create and
delete queues with :meth:`~openstack.message.v2._proxy.Proxy.create_queue` and
:meth:`~openstack.message.v2._proxy.Proxy.delete_queue`::

    >>> queue = conn.message.create_queue(name='my-queue')
    >>> for queue in conn.message.queues():
    ...     print(queue.name)

Working with Messages
---------------------

Producers post messages to a queue with
:meth:`~openstack.message.v2._proxy.Proxy.post_message`, and consumers read
them back with :meth:`~openstack.message.v2._proxy.Proxy.messages`::

    >>> conn.message.post_message(
    ...     queue.name, messages=[{'body': 'hello', 'ttl': 300}])
    >>> for message in conn.message.messages(queue.name):
    ...     print(message.body)

Subscriptions and Claims
------------------------

Subscriptions notify an endpoint when messages arrive; manage them with
:meth:`~openstack.message.v2._proxy.Proxy.create_subscription` and
:meth:`~openstack.message.v2._proxy.Proxy.subscriptions`. Claims let a consumer
reserve a batch of messages for processing; manage them with
:meth:`~openstack.message.v2._proxy.Proxy.create_claim` and the related claim
methods.
