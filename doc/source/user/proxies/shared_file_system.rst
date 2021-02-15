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
  :members: shares, get_share, delete_share, update_share, create_share
