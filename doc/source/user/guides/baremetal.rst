Using OpenStack Baremetal
=========================

Before working with the Bare Metal service, you'll need to create a
connection to your OpenStack cloud by following the :doc:`connect` user
guide. This will provide you with the ``conn`` variable used in the examples
below.

.. contents:: Table of Contents
   :local:

The primary resource of the Bare Metal service is the **node**.

Below are a few usage examples. For a reference to all the available methods,
see :doc:`/user/proxies/baremetal`.

CRUD operations
~~~~~~~~~~~~~~~

List Nodes
----------

A **node** is a bare metal machine.

.. literalinclude:: ../examples/baremetal/list.py
   :pyobject: list_nodes

Full example: `baremetal resource list`_

Provisioning operations
~~~~~~~~~~~~~~~~~~~~~~~

Provisioning actions are the main way to manipulate the nodes. See `Bare Metal
service states documentation`_ for details.

Manage and inspect Node
-----------------------

*Managing* a node in the ``enroll`` provision state validates the management
(IPMI, Redfish, etc) credentials and moves the node to the ``manageable``
state. *Managing* a node in the ``available`` state moves it to the
``manageable`` state. In this state additional actions, such as configuring
RAID or inspecting, are available.

*Inspecting* a node detects its properties by either talking to its BMC or by
booting a special ramdisk.

.. literalinclude:: ../examples/baremetal/provisioning.py
   :pyobject: manage_and_inspect_node

Full example: `baremetal provisioning`_

Provide Node
------------

*Providing* a node in the ``manageable`` provision state makes it available
for deployment.

.. literalinclude:: ../examples/baremetal/provisioning.py
   :pyobject: provide_node

Full example: `baremetal provisioning`_


.. _baremetal resource list: http://opendev.org/openstack/openstacksdk/src/branch/master/examples/baremetal/list.py
.. _baremetal provisioning: http://opendev.org/openstack/openstacksdk/src/branch/master/examples/baremetal/provisioning.py
.. _Bare Metal service states documentation: https://docs.openstack.org/ironic/latest/contributor/states.html
