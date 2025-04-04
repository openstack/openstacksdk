Block Storage API
=================

For details on how to use block_storage, see :doc:`/user/guides/block_storage`

.. automodule:: openstack.block_storage.v2._proxy

The BlockStorage Class
----------------------

The block_storage high-level interface is available through the
``block_storage`` member of a :class:`~openstack.connection.Connection` object.
The ``block_storage`` member will only be added if the service is detected.

Backup Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: create_backup, delete_backup, get_backup, backups, restore_backup,
            reset_backup_status

Capabilities Operations
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: get_capabilities

Limits Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: get_limits

QuotaClassSet Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: get_quota_class_set, update_quota_class_set

QuotaSet Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: get_quota_set, get_quota_set_defaults,
            revert_quota_set, update_quota_set

Service Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
   :noindex:
   :members: find_service, services, enable_service, disable_service,
             thaw_service, freeze_service, failover_service

Snapshot Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: create_snapshot, delete_snapshot, get_snapshot, snapshots,
            reset_snapshot_status

Stats Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: backend_pools

Transfer Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: create_transfer, delete_transfer, find_transfer,
            get_transfer, transfers, accept_transfer

Type Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: create_type, delete_type, get_type, types

Volume Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
  :noindex:
  :members: create_volume, delete_volume, get_volume,
            find_volume, volumes, get_volume_metadata, set_volume_metadata,
            delete_volume_metadata, extend_volume,
            retype_volume, set_volume_bootable_status, reset_volume_status,
            set_volume_image_metadata, delete_volume_image_metadata,
            attach_volume, detach_volume,
            unmanage_volume, migrate_volume, complete_volume_migration

Helpers
^^^^^^^

.. autoclass:: openstack.block_storage.v2._proxy.Proxy
   :noindex:
   :members: wait_for_status, wait_for_delete
