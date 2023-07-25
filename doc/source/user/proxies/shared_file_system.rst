Shared File System API
======================

.. automodule:: openstack.shared_file_system.v2._proxy

The Shared File System Class
----------------------------

The high-level interface for accessing the shared file systems service API is
available through the ``shared_file_system`` member of a :class:`~openstack
.connection.Connection` object. The ``shared_file_system`` member will only
be added if the service is detected. ``share`` is an alias of the
``shared_file_system`` member.


Shared File System Availability Zones
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Interact with Availability Zones supported by the Shared File Systems
service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: availability_zones


Shared File System Shares
^^^^^^^^^^^^^^^^^^^^^^^^^

Interact with Shares supported by the Shared File Systems
service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: shares, get_share, delete_share, update_share, create_share,
            revert_share_to_snapshot, resize_share, find_share, manage_share,
            unmanage_share


Shared File System Storage Pools
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Interact with the storage pool statistics exposed by the Shared File
Systems Service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: storage_pools


Shared File System User Messages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

View and manipulate asynchronous user messages emitted by the Shared
File Systems service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: user_messages, get_user_message, delete_user_message


Shared File System Limits
^^^^^^^^^^^^^^^^^^^^^^^^^

Get absolute limits of resources supported by the Shared File Systems
service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: limits


Shared File System Snapshots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Interact with Share Snapshots supported by the Shared File Systems
service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: share_snapshots, get_share_snapshot, delete_share_snapshot,
            update_share_snapshot, create_share_snapshot

Shared File System Share Snapshot Instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Interact with Share Snapshot Instances supported by the
Shared File Systems service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: share_snapshot_instances, get_share_snapshot_instance


Shared File System Share Networks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create and manipulate Share Networks with the Shared File Systems service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: share_networks, get_share_network, delete_share_network,
            update_share_network, create_share_network


Shared File System Share Instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Administrators can list, show information for, explicitly set the
state of, and force-delete share instances within the Shared File
Systems Service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: share_instances, get_share_instance,
            reset_share_instance_status,
            delete_share_instance


Shared File System Share Network Subnets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create and manipulate Share Network Subnets with the Shared File Systems
service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: share_network_subnets, get_share_network_subnet,
            create_share_network_subnet, delete_share_network_subnet


Shared File System Share Access Rules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create, View, and Delete access rules for shares from the
Shared File Systems service. Access rules can also have their deletion
and visibility restricted during creation. A lock reason can also be
specified. The deletion restriction can be removed during the access removal.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: access_rules, get_access_rule, create_access_rule,
            delete_access_rule


Shared File System Share Groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Interact with Share groups supported by the Shared File Systems
service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: share_groups, get_share_group, delete_share_group,
            update_share_group, create_share_group, find_share_group


Shared File System Share Group Snapshots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Interact with Share Group Snapshots by the Shared File Systems
service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: share_group_snapshots, get_share_group_snapshot, create_share_group_snapshot,
            reset_share_group_snapshot_status, update_share_group_snapshot,
            delete_share_group_snapshot


Shared File System Share Metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

List, Get, Create, Update, and Delete metadata for shares from the
Shared File Systems service.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: get_share_metadata, get_share_metadata_item,
            create_share_metadata, update_share_metadata,
            delete_share_metadata


Shared File System Resource Locks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create, list, update and delete locks for resources. When a resource is
locked, it means that it can be deleted only by services, admins or
the user that created the lock.

.. autoclass:: openstack.shared_file_system.v2._proxy.Proxy
  :noindex:
  :members: resource_locks, get_resource_lock, update_resource_lock,
            delete_resource_lock, create_resource_lock
