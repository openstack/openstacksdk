Block Store API
===============

For details on how to use block_store, see :doc:`/users/guides/block_store`

.. automodule:: openstack.block_store.v2._proxy

The BlockStore Class
--------------------

The block_store high-level interface is available through the ``block_store``
member of a :class:`~openstack.connection.Connection` object.
The ``block_store`` member will only be added if the service is detected.

.. autoclass:: openstack.block_store.v2._proxy.Proxy
   :members:
