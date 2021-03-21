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
  :noindex:
  :members: create_volume, delete_volume, get_volume, volumes

Backup Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: create_backup, delete_backup, get_backup, backups, restore_backup

Type Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: create_type, delete_type, get_type, types

Snapshot Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: create_snapshot, delete_snapshot, get_snapshot, snapshots

Stats Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: backend_pools
