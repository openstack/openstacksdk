KeyManagement API
=================

For details on how to use key_management, see
:doc:`/users/userguides/key_management`

.. automodule:: openstack.key_management.v1._proxy

The KeyManagement Class
-----------------------

The key_management high-level interface is available through the
``key_management`` member of a :class:`~openstack.connection.Connection`
object.  The ``key_management`` member will only be added if the service is
detected.

.. autoclass:: openstack.key_management.v1._proxy.Proxy
   :members:
