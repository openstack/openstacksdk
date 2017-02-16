Message API v1
==============

For details on how to use message, see :doc:`/users/guides/message`

.. automodule:: openstack.message.v1._proxy

The Message v1 Class
--------------------

The message high-level interface is available through the ``message`` member
of a :class:`~openstack.connection.Connection` object.  The ``message``
member will only be added if the service is detected.

Message Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.message.v1._proxy.Proxy

   .. automethod:: openstack.message.v1._proxy.Proxy.claim_messages
   .. automethod:: openstack.message.v1._proxy.Proxy.create_messages
   .. automethod:: openstack.message.v1._proxy.Proxy.delete_message

Queue Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.message.v1._proxy.Proxy

   .. automethod:: openstack.message.v1._proxy.Proxy.create_queue
   .. automethod:: openstack.message.v1._proxy.Proxy.delete_queue
