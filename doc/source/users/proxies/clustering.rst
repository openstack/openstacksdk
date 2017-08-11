Cluster API
===========

.. automodule:: openstack.clustering.v1._proxy

The Cluster Class
-----------------

The cluster high-level interface is available through the ``cluster``
member of a :class:`~openstack.connection.Connection` object.  The
``cluster`` member will only be added if the service is detected.


Build Info Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy

   .. automethod:: openstack.clustering.v1._proxy.Proxy.get_build_info


Profile Type Operations
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy

   .. automethod:: openstack.clustering.v1._proxy.Proxy.profile_types
   .. automethod:: openstack.clustering.v1._proxy.Proxy.get_profile_type


Profile Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy

   .. automethod:: openstack.clustering.v1._proxy.Proxy.create_profile
   .. automethod:: openstack.clustering.v1._proxy.Proxy.update_profile
   .. automethod:: openstack.clustering.v1._proxy.Proxy.delete_profile
   .. automethod:: openstack.clustering.v1._proxy.Proxy.get_profile
   .. automethod:: openstack.clustering.v1._proxy.Proxy.find_profile
   .. automethod:: openstack.clustering.v1._proxy.Proxy.profiles

   .. automethod:: openstack.clustering.v1._proxy.Proxy.validate_profile


Policy Type Operations
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy

   .. automethod:: openstack.clustering.v1._proxy.Proxy.policy_types
   .. automethod:: openstack.clustering.v1._proxy.Proxy.get_policy_type


Policy Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy

   .. automethod:: openstack.clustering.v1._proxy.Proxy.create_policy
   .. automethod:: openstack.clustering.v1._proxy.Proxy.update_policy
   .. automethod:: openstack.clustering.v1._proxy.Proxy.delete_policy
   .. automethod:: openstack.clustering.v1._proxy.Proxy.get_policy
   .. automethod:: openstack.clustering.v1._proxy.Proxy.find_policy
   .. automethod:: openstack.clustering.v1._proxy.Proxy.policies

   .. automethod:: openstack.clustering.v1._proxy.Proxy.validate_policy


Cluster Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy

   .. automethod:: openstack.clustering.v1._proxy.Proxy.create_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.update_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.delete_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.get_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.find_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.clusters

   .. automethod:: openstack.clustering.v1._proxy.Proxy.check_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.recover_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.resize_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.scale_in_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.scale_out_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.collect_cluster_attrs
   .. automethod:: openstack.clustering.v1._proxy.Proxy.perform_operation_on_cluster

   .. automethod:: openstack.clustering.v1._proxy.Proxy.add_nodes_to_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.remove_nodes_from_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.replace_nodes_in_cluster

   .. automethod:: openstack.clustering.v1._proxy.Proxy.attach_policy_to_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.update_cluster_policy
   .. automethod:: openstack.clustering.v1._proxy.Proxy.detach_policy_from_cluster
   .. automethod:: openstack.clustering.v1._proxy.Proxy.get_cluster_policy
   .. automethod:: openstack.clustering.v1._proxy.Proxy.cluster_policies

   .. automethod:: openstack.clustering.v1._proxy.Proxy.cluster_add_nodes
   .. automethod:: openstack.clustering.v1._proxy.Proxy.cluster_attach_policy
   .. automethod:: openstack.clustering.v1._proxy.Proxy.cluster_del_nodes
   .. automethod:: openstack.clustering.v1._proxy.Proxy.cluster_detach_policy
   .. automethod:: openstack.clustering.v1._proxy.Proxy.cluster_operation
   .. automethod:: openstack.clustering.v1._proxy.Proxy.cluster_replace_nodes
   .. automethod:: openstack.clustering.v1._proxy.Proxy.cluster_resize
   .. automethod:: openstack.clustering.v1._proxy.Proxy.cluster_scale_in
   .. automethod:: openstack.clustering.v1._proxy.Proxy.cluster_scale_out
   .. automethod:: openstack.clustering.v1._proxy.Proxy.cluster_update_policy


Node Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy

   .. automethod:: openstack.clustering.v1._proxy.Proxy.create_node
   .. automethod:: openstack.clustering.v1._proxy.Proxy.update_node
   .. automethod:: openstack.clustering.v1._proxy.Proxy.delete_node
   .. automethod:: openstack.clustering.v1._proxy.Proxy.get_node
   .. automethod:: openstack.clustering.v1._proxy.Proxy.find_node
   .. automethod:: openstack.clustering.v1._proxy.Proxy.nodes

   .. automethod:: openstack.clustering.v1._proxy.Proxy.check_node
   .. automethod:: openstack.clustering.v1._proxy.Proxy.recover_node
   .. automethod:: openstack.clustering.v1._proxy.Proxy.perform_operation_on_node

   .. automethod:: openstack.clustering.v1._proxy.Proxy.adopt_node
   .. automethod:: openstack.clustering.v1._proxy.Proxy.node_operation


Receiver Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy

   .. automethod:: openstack.clustering.v1._proxy.Proxy.create_receiver
   .. automethod:: openstack.clustering.v1._proxy.Proxy.update_receiver
   .. automethod:: openstack.clustering.v1._proxy.Proxy.delete_receiver
   .. automethod:: openstack.clustering.v1._proxy.Proxy.get_receiver
   .. automethod:: openstack.clustering.v1._proxy.Proxy.find_receiver
   .. automethod:: openstack.clustering.v1._proxy.Proxy.receivers


Action Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy

   .. automethod:: openstack.clustering.v1._proxy.Proxy.get_action
   .. automethod:: openstack.clustering.v1._proxy.Proxy.actions


Event Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy

   .. automethod:: openstack.clustering.v1._proxy.Proxy.get_event
   .. automethod:: openstack.clustering.v1._proxy.Proxy.events


Helper Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy

   .. automethod:: openstack.clustering.v1._proxy.Proxy.wait_for_delete
   .. automethod:: openstack.clustering.v1._proxy.Proxy.wait_for_status


Service Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy

   .. automethod:: openstack.clustering.v1._proxy.Proxy.services
