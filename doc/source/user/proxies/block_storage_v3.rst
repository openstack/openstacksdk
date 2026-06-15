Block Storage API
=================

For details on how to use block_storage, see :doc:`/user/guides/block_storage`

.. automodule:: openstack.block_storage.v3._proxy

The BlockStorage Class
----------------------

The block_storage high-level interface is available through the
``block_storage`` member of a :class:`~openstack.connection.Connection` object.
The ``block_storage`` member will only be added if the service is detected.

Attachments
^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: create_attachment, get_attachment, attachments,
            delete_attachment, update_attachment, complete_attachment

Availability Zone Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: availability_zones

Backend Pools Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: backend_pools

Backup Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: create_backup, delete_backup, update_backup,
            get_backup, find_backup, backups,
            import_backup, export_backup, export_record,
            restore_backup, reset_backup_status, reset_backup,
            fetch_backup_metadata, get_backup_metadata,
            set_backup_metadata, delete_backup_metadata

BlockStorageSummary Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: summary

Capabilities Operations
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: get_capabilities

Consistency Group Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: create_consistency_group, create_consistency_group_from_source,
            delete_consistency_group, update_consistency_group,
            get_consistency_group, find_consistency_group, consistency_groups

Consistency Group Snapshot Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: create_consistency_group_snapshot,
            delete_consistency_group_snapshot,
            get_consistency_group_snapshot,
            find_consistency_group_snapshot, consistency_group_snapshots

Default Volume Types
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: default_types, show_default_type, set_default_type,
            unset_default_type

Extension Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: extensions

Limits Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: get_limits

Group Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: create_group, create_group_from_source, delete_group, update_group,
            get_group, find_group, groups, reset_group_status,
            reset_group_state,
            enable_group_replication, disable_group_replication,
            failover_group_replication

Group Snapshot Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: create_group_snapshot, delete_group_snapshot, get_group_snapshot,
            find_group_snapshot, group_snapshots, reset_group_snapshot_status,
            reset_group_snapshot_state

Group Type Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: create_group_type, delete_group_type, update_group_type,
            get_group_type, find_group_type, group_types,
            fetch_group_type_group_specs, create_group_type_group_specs,
            get_group_type_group_specs_property,
            update_group_type_group_specs_property,
            delete_group_type_group_specs_property

Message Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: get_message, delete_message, messages

QuotaClassSet Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: get_quota_class_set, update_quota_class_set

QuotaSet Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: get_quota_set, get_quota_set_defaults,
            revert_quota_set, update_quota_set

QoSSpec Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: create_qos_spec, delete_qos_spec, find_qos_spec, get_qos_spec,
            qos_specs, update_qos_spec, associate_qos_spec,
            disassociate_qos_spec, disassociate_all_qos_spec,
            delete_qos_spec_metadata, qos_spec_associations

Resource Filter Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: resource_filters

Service Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
   :noindex:
   :members: find_service, services, enable_service, disable_service,
             thaw_service, freeze_service, failover_service,
             get_service_log_levels, set_service_log_levels,
             cleanup_service_workers

Snapshot Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: create_snapshot, delete_snapshot, update_snapshot, get_snapshot,
            find_snapshot, snapshots, get_snapshot_metadata,
            fetch_snapshot_metadata,
            set_snapshot_metadata, delete_snapshot_metadata,
            reset_snapshot_status, reset_snapshot,
            set_snapshot_status, manage_snapshot,
            unmanage_snapshot

Stats Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: backend_pools

Transfer Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: create_transfer, delete_transfer, find_transfer,
            get_transfer, transfers, accept_transfer

Type Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: create_type, delete_type, update_type, get_type, find_type, types,
            update_type_extra_specs, delete_type_extra_specs, get_type_access,
            add_type_access, remove_type_access, get_type_encryption,
            create_type_encryption, delete_type_encryption,
            update_type_encryption

Volume Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: create_volume, delete_volume, update_volume, get_volume,
            find_volume, volumes, get_volume_metadata, fetch_volume_metadata,
            set_volume_metadata,
            delete_volume_metadata, extend_volume, complete_volume_extend,
            set_volume_readonly,
            retype_volume, set_volume_bootable_status, reset_volume_status,
            set_volume_image_metadata, delete_volume_image_metadata,
            revert_volume_to_snapshot, attach_volume, detach_volume,
            unmanage_volume, migrate_volume, complete_volume_migration,
            upload_volume_to_image, create_image,
            reserve_volume, unreserve_volume,
            begin_volume_detaching, abort_volume_detaching,
            init_volume_attachment, terminate_volume_attachment,
            manage_volume,

Helpers
^^^^^^^

.. autoclass:: openstack.block_storage.v3._proxy.Proxy
  :noindex:
  :members: wait_for_status, wait_for_delete
