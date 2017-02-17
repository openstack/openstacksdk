Identity API v3
===============

For details on how to use identity, see :doc:`/users/guides/identity`

.. automodule:: openstack.identity.v3._proxy

The Identity v3 Class
---------------------

The identity high-level interface is available through the ``identity``
member of a :class:`~openstack.connection.Connection` object.  The
``identity`` member will only be added if the service is detected.

Credential Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy

   .. automethod:: openstack.identity.v3._proxy.Proxy.create_credential
   .. automethod:: openstack.identity.v3._proxy.Proxy.update_credential
   .. automethod:: openstack.identity.v3._proxy.Proxy.delete_credential
   .. automethod:: openstack.identity.v3._proxy.Proxy.get_credential
   .. automethod:: openstack.identity.v3._proxy.Proxy.find_credential
   .. automethod:: openstack.identity.v3._proxy.Proxy.credentials

Domain Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy

   .. automethod:: openstack.identity.v3._proxy.Proxy.create_domain
   .. automethod:: openstack.identity.v3._proxy.Proxy.update_domain
   .. automethod:: openstack.identity.v3._proxy.Proxy.delete_domain
   .. automethod:: openstack.identity.v3._proxy.Proxy.get_domain
   .. automethod:: openstack.identity.v3._proxy.Proxy.find_domain
   .. automethod:: openstack.identity.v3._proxy.Proxy.domains

Endpoint Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy

   .. automethod:: openstack.identity.v3._proxy.Proxy.create_endpoint
   .. automethod:: openstack.identity.v3._proxy.Proxy.update_endpoint
   .. automethod:: openstack.identity.v3._proxy.Proxy.delete_endpoint
   .. automethod:: openstack.identity.v3._proxy.Proxy.get_endpoint
   .. automethod:: openstack.identity.v3._proxy.Proxy.find_endpoint
   .. automethod:: openstack.identity.v3._proxy.Proxy.endpoints

Group Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy

   .. automethod:: openstack.identity.v3._proxy.Proxy.create_group
   .. automethod:: openstack.identity.v3._proxy.Proxy.update_group
   .. automethod:: openstack.identity.v3._proxy.Proxy.delete_group
   .. automethod:: openstack.identity.v3._proxy.Proxy.get_group
   .. automethod:: openstack.identity.v3._proxy.Proxy.find_group
   .. automethod:: openstack.identity.v3._proxy.Proxy.groups

Policy Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy

   .. automethod:: openstack.identity.v3._proxy.Proxy.create_policy
   .. automethod:: openstack.identity.v3._proxy.Proxy.update_policy
   .. automethod:: openstack.identity.v3._proxy.Proxy.delete_policy
   .. automethod:: openstack.identity.v3._proxy.Proxy.get_policy
   .. automethod:: openstack.identity.v3._proxy.Proxy.find_policy
   .. automethod:: openstack.identity.v3._proxy.Proxy.policies

Project Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy

   .. automethod:: openstack.identity.v3._proxy.Proxy.create_project
   .. automethod:: openstack.identity.v3._proxy.Proxy.update_project
   .. automethod:: openstack.identity.v3._proxy.Proxy.delete_project
   .. automethod:: openstack.identity.v3._proxy.Proxy.get_project
   .. automethod:: openstack.identity.v3._proxy.Proxy.find_project
   .. automethod:: openstack.identity.v3._proxy.Proxy.projects

Region Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy

   .. automethod:: openstack.identity.v3._proxy.Proxy.create_region
   .. automethod:: openstack.identity.v3._proxy.Proxy.update_region
   .. automethod:: openstack.identity.v3._proxy.Proxy.delete_region
   .. automethod:: openstack.identity.v3._proxy.Proxy.get_region
   .. automethod:: openstack.identity.v3._proxy.Proxy.find_region
   .. automethod:: openstack.identity.v3._proxy.Proxy.regions

Role Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy

   .. automethod:: openstack.identity.v3._proxy.Proxy.create_role
   .. automethod:: openstack.identity.v3._proxy.Proxy.update_role
   .. automethod:: openstack.identity.v3._proxy.Proxy.delete_role
   .. automethod:: openstack.identity.v3._proxy.Proxy.get_role
   .. automethod:: openstack.identity.v3._proxy.Proxy.find_role
   .. automethod:: openstack.identity.v3._proxy.Proxy.roles
   .. automethod:: openstack.identity.v3._proxy.Proxy.role_assignments
   .. automethod:: openstack.identity.v3._proxy.Proxy.role_assignments_filter

Service Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy

   .. automethod:: openstack.identity.v3._proxy.Proxy.create_service
   .. automethod:: openstack.identity.v3._proxy.Proxy.update_service
   .. automethod:: openstack.identity.v3._proxy.Proxy.delete_service
   .. automethod:: openstack.identity.v3._proxy.Proxy.get_service
   .. automethod:: openstack.identity.v3._proxy.Proxy.find_service
   .. automethod:: openstack.identity.v3._proxy.Proxy.services

Trust Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy

   .. automethod:: openstack.identity.v3._proxy.Proxy.create_trust
   .. automethod:: openstack.identity.v3._proxy.Proxy.delete_trust
   .. automethod:: openstack.identity.v3._proxy.Proxy.get_trust
   .. automethod:: openstack.identity.v3._proxy.Proxy.find_trust
   .. automethod:: openstack.identity.v3._proxy.Proxy.trusts

User Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy

   .. automethod:: openstack.identity.v3._proxy.Proxy.create_user
   .. automethod:: openstack.identity.v3._proxy.Proxy.update_user
   .. automethod:: openstack.identity.v3._proxy.Proxy.delete_user
   .. automethod:: openstack.identity.v3._proxy.Proxy.get_user
   .. automethod:: openstack.identity.v3._proxy.Proxy.find_user
   .. automethod:: openstack.identity.v3._proxy.Proxy.users
