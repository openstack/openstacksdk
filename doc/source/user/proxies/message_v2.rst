Message API v2
==============

For details on how to use message, see :doc:`/user/guides/message`

.. automodule:: openstack.message.v2._proxy

The Message v2 Class
--------------------

The message high-level interface is available through the ``message`` member
of a :class:`~openstack.connection.Connection` object.  The ``message``
member will only be added if the service is detected.

Message Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.message.v2._proxy.Proxy
  :noindex:
  :members: post_message, delete_message, get_message, messages

Queue Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.message.v2._proxy.Proxy
  :noindex:
  :members: create_queue, delete_queue, get_queue, queues

Claim Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.message.v2._proxy.Proxy
  :noindex:
  :members: create_claim, update_claim, delete_claim, get_claim

Subscription Operations
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.message.v2._proxy.Proxy
  :noindex:
  :members: create_subscription, delete_subscription, get_subscription,
            subscriptions
