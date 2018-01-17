Block Storage API
=================

For details on how to use block_storage, see :doc:`/user/guides/block_storage`

.. automodule:: openstack.block_storage.v2._proxy

The BlockStorage Class
----------------------

The block_storage high-level interface is available through the
``block_storage`` member of a :class:`~openstack.connection.Connection` object.
The ``block_storage`` member will only be added if the service is detected.

Volume Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy

   .. automethod:: openstack.block_storage.v2._proxy.Proxy.create_volume
   .. automethod:: openstack.block_storage.v2._proxy.Proxy.delete_volume
   .. automethod:: openstack.block_storage.v2._proxy.Proxy.get_volume
   .. automethod:: openstack.block_storage.v2._proxy.Proxy.volumes

Type Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy

   .. automethod:: openstack.block_storage.v2._proxy.Proxy.create_type
   .. automethod:: openstack.block_storage.v2._proxy.Proxy.delete_type
   .. automethod:: openstack.block_storage.v2._proxy.Proxy.get_type
   .. automethod:: openstack.block_storage.v2._proxy.Proxy.types

Snapshot Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy

   .. automethod:: openstack.block_storage.v2._proxy.Proxy.create_snapshot
   .. automethod:: openstack.block_storage.v2._proxy.Proxy.delete_snapshot
   .. automethod:: openstack.block_storage.v2._proxy.Proxy.get_snapshot
   .. automethod:: openstack.block_storage.v2._proxy.Proxy.snapshots

Stats Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy

   .. automethod:: openstack.block_storage.v2._proxy.Proxy.backend_pools
