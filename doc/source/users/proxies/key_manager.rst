KeyManager API
==============

For details on how to use key_management, see
:doc:`/users/guides/key_manager`

.. automodule:: openstack.key_manager.v1._proxy

The KeyManager Class
--------------------

The key_management high-level interface is available through the
``key_manager`` member of a :class:`~openstack.connection.Connection`
object.  The ``key_manager`` member will only be added if the service is
detected.

Secret Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.key_manager.v1._proxy.Proxy

   .. automethod:: openstack.key_manager.v1._proxy.Proxy.create_secret
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.update_secret
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.delete_secret
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.get_secret
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.find_secret
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.secrets

Container Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.key_manager.v1._proxy.Proxy

   .. automethod:: openstack.key_manager.v1._proxy.Proxy.create_container
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.update_container
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.delete_container
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.get_container
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.find_container
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.containers

Order Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.key_manager.v1._proxy.Proxy

   .. automethod:: openstack.key_manager.v1._proxy.Proxy.create_order
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.update_order
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.delete_order
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.get_order
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.find_order
   .. automethod:: openstack.key_manager.v1._proxy.Proxy.orders
