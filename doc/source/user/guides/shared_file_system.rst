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
