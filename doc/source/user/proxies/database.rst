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
  :noindex:
  :members: create_database, delete_database, get_database, find_database,
            databases

Flavor Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.database.v1._proxy.Proxy
  :noindex:
  :members: get_flavor, find_flavor, flavors

Instance Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.database.v1._proxy.Proxy
  :noindex:
  :members: create_instance, update_instance, delete_instance, get_instance,
            find_instance, instances

User Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.database.v1._proxy.Proxy
  :noindex:
  :members: create_user, delete_user, get_user, find_user, users
