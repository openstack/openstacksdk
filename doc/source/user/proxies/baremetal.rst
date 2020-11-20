Baremetal API
=============

For details on how to use baremetal, see :doc:`/user/guides/baremetal`

.. automodule:: openstack.baremetal.v1._proxy

The Baremetal Class
-------------------

The baremetal high-level interface is available through the ``baremetal``
member of a :class:`~openstack.connection.Connection` object.
The ``baremetal`` member will only be added if the service is detected.

Node Operations
^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy
  :noindex:
  :members: nodes, find_node, get_node, create_node, update_node, patch_node, delete_node,
            validate_node, set_node_power_state, set_node_provision_state,
            wait_for_nodes_provision_state, wait_for_node_power_state,
            wait_for_node_reservation, set_node_maintenance, unset_node_maintenance

Port Operations
^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy
  :noindex:
  :members: ports, find_port, get_port, create_port, update_port, delete_port, patch_port

Port Group Operations
^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy
  :noindex:
  :members: port_groups, find_port_group, get_port_group,
            create_port_group, update_port_group, delete_port_group, patch_port_group

Driver Operations
^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy
  :noindex:
  :members: drivers, get_driver

Chassis Operations
^^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy
  :noindex:
  :members: chassis, find_chassis, get_chassis,
            create_chassis, update_chassis, patch_chassis, delete_chassis

VIF Operations
^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy
  :noindex:
  :members: list_node_vifs, attach_vif_to_node, detach_vif_from_node

Allocation Operations
^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy
  :noindex:
  :members: allocations, get_allocation, create_allocation,
            update_allocation, patch_allocation, delete_allocation,
            wait_for_allocation

Volume Connector Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy
  :noindex:
  :members: volume_connectors, find_volume_connector, get_volume_connector,
            create_volume_connector, update_volume_connector,
            patch_volume_connector, delete_volume_connector

Volume Target Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: openstack.baremetal.v1._proxy.Proxy
  :noindex:
  :members: volume_targets, find_volume_target, get_volume_target,
            create_volume_target, update_volume_target,
            patch_volume_target, delete_volume_target

Utilities
---------

Building config drives
^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: openstack.baremetal.configdrive
  :noindex:
   :members:
