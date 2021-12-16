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
            revert_share_to_snapshot


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
