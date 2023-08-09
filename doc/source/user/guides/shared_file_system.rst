Using OpenStack Shared File Systems
===================================

Before working with the Shared File System service, you'll need to create a
connection to your OpenStack cloud by following the :doc:`connect` user
guide. This will provide you with the ``conn`` variable used in the examples
below.

.. contents:: Table of Contents
   :local:


List Availability Zones
-----------------------

A Shared File System service **availability zone** is a failure domain for
your shared file systems. You may create a shared file system (referred
to simply as **shares**) in a given availability zone, and create replicas
of the share in other availability zones.

.. literalinclude:: ../examples/shared_file_system/availability_zones.py
   :pyobject: list_availability_zones


Share Instances
---------------

Administrators can list, show information for, explicitly set the state of,
and force-delete share instances.

.. literalinclude:: ../examples/shared_file_system/share_instances.py
   :pyobject: share_instances


Get Share Instance
------------------

Shows details for a single share instance.

.. literalinclude:: ../examples/shared_file_system/share_instances.py
   :pyobject: get_share_instance


Reset Share Instance Status
---------------------------

Explicitly updates the state of a share instance.

.. literalinclude:: ../examples/shared_file_system/share_instances.py
   :pyobject: reset_share_instance_status


Delete Share Instance
---------------------

Force-deletes a share instance.

.. literalinclude:: ../examples/shared_file_system/share_instances.py
   :pyobject: delete_share_instance


Resize Share
------------

Shared File System shares can be resized (extended or shrunk) to a given
size. For details on resizing shares, refer to the
`Manila docs <https://docs.openstack.org/manila/latest/user/create-and-manage-shares.html#extend-share>`_.

.. literalinclude:: ../examples/shared_file_system/shares.py
   :pyobject: resize_share
.. literalinclude:: ../examples/shared_file_system/shares.py
   :pyobject: resize_shares_without_shrink


List Share Group Snapshots
--------------------------

A share group snapshot is a point-in-time, read-only copy of the data that is
contained in a share group. You can list all share group snapshots

.. literalinclude:: ../examples/shared_file_system/share_group_snapshots.py
   :pyobject: list_share_group_snapshots


Get Share Group Snapshot
------------------------

Show share group snapshot details

.. literalinclude:: ../examples/shared_file_system/share_group_snapshots.py
   :pyobject: get_share_group_snapshot


List Share Group Snapshot Members
---------------------------------

Lists all share group snapshots members.

.. literalinclude:: ../examples/shared_file_system/share_group_snapshots.py
   :pyobject: share_group_snapshot_members


Create Share Group Snapshot
---------------------------

Creates a snapshot from a share group.

.. literalinclude:: ../examples/shared_file_system/share_group_snapshots.py
   :pyobject: create_share_group_snapshot


Reset Share Group Snapshot
---------------------------

Reset share group snapshot state.

.. literalinclude:: ../examples/shared_file_system/share_group_snapshots.py
   :pyobject: reset_share_group_snapshot_status


Update Share Group Snapshot
---------------------------

Updates a share group snapshot.

.. literalinclude:: ../examples/shared_file_system/share_group_snapshots.py
   :pyobject: update_share_group_snapshot


Delete Share Group Snapshot
---------------------------

Deletes a share group snapshot.

.. literalinclude:: ../examples/shared_file_system/share_group_snapshots.py
   :pyobject: delete_share_group_snapshot


List Share Metadata
--------------------

Lists all metadata for a given share.

.. literalinclude:: ../examples/shared_file_system/share_metadata.py
   :pyobject: list_share_metadata


Get Share Metadata Item
-----------------------

Retrieves a specific metadata item from a shares metadata by its key.

.. literalinclude:: ../examples/shared_file_system/share_metadata.py
   :pyobject: get_share_metadata_item


Create Share Metadata
----------------------

Creates share metadata.

.. literalinclude:: ../examples/shared_file_system/share_metadata.py
   :pyobject: create_share_metadata


Update Share Metadata
----------------------

Updates metadata of a given share.

.. literalinclude:: ../examples/shared_file_system/share_metadata.py
   :pyobject: update_share_metadata


Delete Share Metadata
----------------------

Deletes a specific metadata item from a shares metadata by its key. Can
specify multiple keys to be deleted.

.. literalinclude:: ../examples/shared_file_system/share_metadata.py
   :pyobject: delete_share_metadata


Manage Share
------------

Manage a share with Manila.

.. literalinclude:: ../examples/shared_file_system/shares.py
   :pyobject: manage_share


Unmanage Share
--------------

Unmanage a share from Manila.

.. literalinclude:: ../examples/shared_file_system/shares.py
   :pyobject: unmanage_share
