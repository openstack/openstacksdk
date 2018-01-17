Database API
============

For details on how to use database, see :doc:`/user/guides/database`

.. automodule:: openstack.database.v1._proxy

The Database Class
------------------

The database high-level interface is available through the ``database``
member of a :class:`~openstack.connection.Connection` object.  The
``database`` member will only be added if the service is detected.

Database Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.database.v1._proxy.Proxy

   .. automethod:: openstack.database.v1._proxy.Proxy.create_database
   .. automethod:: openstack.database.v1._proxy.Proxy.delete_database
   .. automethod:: openstack.database.v1._proxy.Proxy.get_database
   .. automethod:: openstack.database.v1._proxy.Proxy.find_database
   .. automethod:: openstack.database.v1._proxy.Proxy.databases

Flavor Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.database.v1._proxy.Proxy

   .. automethod:: openstack.database.v1._proxy.Proxy.get_flavor
   .. automethod:: openstack.database.v1._proxy.Proxy.find_flavor
   .. automethod:: openstack.database.v1._proxy.Proxy.flavors

Instance Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.database.v1._proxy.Proxy

   .. automethod:: openstack.database.v1._proxy.Proxy.create_instance
   .. automethod:: openstack.database.v1._proxy.Proxy.update_instance
   .. automethod:: openstack.database.v1._proxy.Proxy.delete_instance
   .. automethod:: openstack.database.v1._proxy.Proxy.get_instance
   .. automethod:: openstack.database.v1._proxy.Proxy.find_instance
   .. automethod:: openstack.database.v1._proxy.Proxy.instances

User Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.database.v1._proxy.Proxy

   .. automethod:: openstack.database.v1._proxy.Proxy.create_user
   .. automethod:: openstack.database.v1._proxy.Proxy.delete_user
   .. automethod:: openstack.database.v1._proxy.Proxy.get_user
   .. automethod:: openstack.database.v1._proxy.Proxy.find_user
   .. automethod:: openstack.database.v1._proxy.Proxy.users
