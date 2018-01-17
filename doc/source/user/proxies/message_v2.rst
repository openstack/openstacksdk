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

   .. automethod:: openstack.message.v2._proxy.Proxy.post_message
   .. automethod:: openstack.message.v2._proxy.Proxy.delete_message
   .. automethod:: openstack.message.v2._proxy.Proxy.get_message
   .. automethod:: openstack.message.v2._proxy.Proxy.messages

Queue Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.message.v2._proxy.Proxy

   .. automethod:: openstack.message.v2._proxy.Proxy.create_queue
   .. automethod:: openstack.message.v2._proxy.Proxy.delete_queue
   .. automethod:: openstack.message.v2._proxy.Proxy.get_queue
   .. automethod:: openstack.message.v2._proxy.Proxy.queues

Claim Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.message.v2._proxy.Proxy

   .. automethod:: openstack.message.v2._proxy.Proxy.create_claim
   .. automethod:: openstack.message.v2._proxy.Proxy.update_claim
   .. automethod:: openstack.message.v2._proxy.Proxy.delete_claim
   .. automethod:: openstack.message.v2._proxy.Proxy.get_claim

Subscription Operations
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.message.v2._proxy.Proxy

   .. automethod:: openstack.message.v2._proxy.Proxy.create_subscription
   .. automethod:: openstack.message.v2._proxy.Proxy.delete_subscription
   .. automethod:: openstack.message.v2._proxy.Proxy.get_subscription
   .. automethod:: openstack.message.v2._proxy.Proxy.subscriptions
