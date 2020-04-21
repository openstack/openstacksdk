KeyManager API
==============

For details on how to use key_management, see
:doc:`/user/guides/key_manager`

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
  :noindex:
  :members: create_secret, update_secret, delete_secret, get_secret,
            find_secret, secrets

Container Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.key_manager.v1._proxy.Proxy
  :noindex:
  :members: create_container, update_container, delete_container,
            get_container, find_container, containers

Order Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.key_manager.v1._proxy.Proxy
  :noindex:
  :members: create_order, update_order, delete_order, get_order,
            find_order, orders
