Identity API v2
===============

For details on how to use identity, see :doc:`/user/guides/identity`

.. automodule:: openstack.identity.v2._proxy

The Identity v2 Class
---------------------

The identity high-level interface is available through the ``identity``
member of a :class:`~openstack.connection.Connection` object.  The
``identity`` member will only be added if the service is detected.

Extension Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v2._proxy.Proxy
  :noindex:
  :members: get_extension, extensions

User Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v2._proxy.Proxy
  :noindex:
  :members: create_user, update_user, delete_user, get_user, find_user, users

Role Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v2._proxy.Proxy
  :noindex:
  :members: create_role, update_role, delete_role, get_role, find_role, roles

Tenant Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v2._proxy.Proxy
  :noindex:
  :members: create_tenant, update_tenant, delete_tenant, get_tenant,
            find_tenant, tenants
