Database API
============

For details on how to use database, see :doc:`/users/guides/database`

.. automodule:: openstack.database.v1._proxy

The Database Class
------------------

The database high-level interface is available through the ``database``
member of a :class:`~openstack.connection.Connection` object.  The
``database`` member will only be added if the service is detected.

.. autoclass:: openstack.database.v1._proxy.Proxy
   :members:
