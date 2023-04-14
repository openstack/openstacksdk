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
