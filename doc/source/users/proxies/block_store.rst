Block Store API
===============

For details on how to use block_store, see :doc:`/users/guides/block_store`

.. automodule:: openstack.block_store.v2._proxy

The BlockStore Class
--------------------

The block_store high-level interface is available through the ``block_store``
member of a :class:`~openstack.connection.Connection` object.
The ``block_store`` member will only be added if the service is detected.

Volume Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_store.v2._proxy.Proxy

   .. automethod:: openstack.block_store.v2._proxy.Proxy.create_volume
   .. automethod:: openstack.block_store.v2._proxy.Proxy.delete_volume
   .. automethod:: openstack.block_store.v2._proxy.Proxy.get_volume
   .. automethod:: openstack.block_store.v2._proxy.Proxy.volumes

Type Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_store.v2._proxy.Proxy

   .. automethod:: openstack.block_store.v2._proxy.Proxy.create_type
   .. automethod:: openstack.block_store.v2._proxy.Proxy.delete_type
   .. automethod:: openstack.block_store.v2._proxy.Proxy.get_type
   .. automethod:: openstack.block_store.v2._proxy.Proxy.types

Snapshot Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_store.v2._proxy.Proxy

   .. automethod:: openstack.block_store.v2._proxy.Proxy.create_snapshot
   .. automethod:: openstack.block_store.v2._proxy.Proxy.delete_snapshot
   .. automethod:: openstack.block_store.v2._proxy.Proxy.get_snapshot
   .. automethod:: openstack.block_store.v2._proxy.Proxy.snapshots
