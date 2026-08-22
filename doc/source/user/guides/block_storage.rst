Using OpenStack Block Storage
=============================

Before working with the Block Storage service, you'll need to create a
connection to your OpenStack cloud by following the :doc:`connect` user
guide. This will provide you with the ``conn`` variable used in the examples
below.

.. contents:: Table of Contents
   :local:

The Block Storage service manages volumes and the snapshots, backups and
volume types associated with them. The examples below show a representative
subset of what is possible; for the complete set of operations, see the
:doc:`Block Storage proxy reference </user/proxies/block_storage_v3>`.

Working with Volumes
--------------------

To list the existing volumes, use the
:meth:`~openstack.block_storage.v3._proxy.Proxy.volumes` method, which returns
a generator of :class:`~openstack.block_storage.v3.volume.Volume` objects::

    >>> for volume in conn.block_storage.volumes():
    ...     print(volume.name, volume.status)

To create a volume, use the
:meth:`~openstack.block_storage.v3._proxy.Proxy.create_volume` method::

    >>> volume = conn.block_storage.create_volume(name='my-volume', size=10)

To retrieve or delete a volume, use the
:meth:`~openstack.block_storage.v3._proxy.Proxy.get_volume` and
:meth:`~openstack.block_storage.v3._proxy.Proxy.delete_volume` methods. Each
accepts either a volume ID or a
:class:`~openstack.block_storage.v3.volume.Volume` instance::

    >>> volume = conn.block_storage.get_volume(volume.id)
    >>> conn.block_storage.delete_volume(volume)

Working with Snapshots and Backups
----------------------------------

A snapshot captures the state of a volume at a point in time. Create one with
:meth:`~openstack.block_storage.v3._proxy.Proxy.create_snapshot`, list them
with :meth:`~openstack.block_storage.v3._proxy.Proxy.snapshots`, and remove
them with :meth:`~openstack.block_storage.v3._proxy.Proxy.delete_snapshot`::

    >>> snapshot = conn.block_storage.create_snapshot(volume_id=volume.id)
    >>> for snapshot in conn.block_storage.snapshots():
    ...     print(snapshot.name)

Backups are managed in the same way through the corresponding ``backups``,
``create_backup`` and ``delete_backup`` methods.

Working with Volume Types
-------------------------

Volume types describe the capabilities of the storage backing a volume. List
the available types with
:meth:`~openstack.block_storage.v3._proxy.Proxy.types`::

    >>> for volume_type in conn.block_storage.types():
    ...     print(volume_type.name)
