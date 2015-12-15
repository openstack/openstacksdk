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

.. autoclass:: openstack.key_manager.v1._proxy.Proxy
   :members:
