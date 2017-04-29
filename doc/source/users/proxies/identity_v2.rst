Identity API v2
===============

For details on how to use identity, see :doc:`/users/guides/identity`

.. automodule:: openstack.identity.v2._proxy

The Identity v2 Class
---------------------

The identity high-level interface is available through the ``identity``
member of a :class:`~openstack.connection.Connection` object.  The
``identity`` member will only be added if the service is detected.

Extension Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v2._proxy.Proxy

   .. automethod:: openstack.identity.v2._proxy.Proxy.get_extension
   .. automethod:: openstack.identity.v2._proxy.Proxy.extensions

User Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v2._proxy.Proxy

   .. automethod:: openstack.identity.v2._proxy.Proxy.create_user
   .. automethod:: openstack.identity.v2._proxy.Proxy.update_user
   .. automethod:: openstack.identity.v2._proxy.Proxy.delete_user
   .. automethod:: openstack.identity.v2._proxy.Proxy.get_user
   .. automethod:: openstack.identity.v2._proxy.Proxy.find_user
   .. automethod:: openstack.identity.v2._proxy.Proxy.users

Role Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v2._proxy.Proxy

   .. automethod:: openstack.identity.v2._proxy.Proxy.create_role
   .. automethod:: openstack.identity.v2._proxy.Proxy.update_role
   .. automethod:: openstack.identity.v2._proxy.Proxy.delete_role
   .. automethod:: openstack.identity.v2._proxy.Proxy.get_role
   .. automethod:: openstack.identity.v2._proxy.Proxy.find_role
   .. automethod:: openstack.identity.v2._proxy.Proxy.roles

Tenant Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v2._proxy.Proxy

   .. automethod:: openstack.identity.v2._proxy.Proxy.create_tenant
   .. automethod:: openstack.identity.v2._proxy.Proxy.update_tenant
   .. automethod:: openstack.identity.v2._proxy.Proxy.delete_tenant
   .. automethod:: openstack.identity.v2._proxy.Proxy.get_tenant
   .. automethod:: openstack.identity.v2._proxy.Proxy.find_tenant
   .. automethod:: openstack.identity.v2._proxy.Proxy.tenants
