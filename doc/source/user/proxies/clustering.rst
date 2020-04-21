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
  :noindex:
  :members: get_build_info


Profile Type Operations
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy
  :noindex:
  :members: profile_types, get_profile_type


Profile Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy
  :noindex:
  :members: create_profile, update_profile, delete_profile, get_profile,
            find_profile, profiles, validate_profile


Policy Type Operations
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy
  :noindex:
  :members: policy_types, get_policy_type


Policy Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy
  :noindex:
  :members: create_policy, update_policy, delete_policy, get_policy,
            find_policy, policies

validate_policy


Cluster Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy
  :noindex:
  :members: create_cluster, update_cluster, delete_cluster, get_cluster,
            find_cluster, clusters, check_cluster, recover_cluster,
            resize_cluster, scale_in_cluster, scale_out_cluster,
            collect_cluster_attrs, perform_operation_on_cluster,
            add_nodes_to_cluster, remove_nodes_from_cluster,
            replace_nodes_in_cluster, attach_policy_to_cluster,
            update_cluster_policy, detach_policy_from_cluster,
            get_cluster_policy, cluster_policies

Node Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy
  :noindex:
  :members: create_node, update_node, delete_node, get_node, find_node, nodes,
            check_node, recover_node, perform_operation_on_node, adopt_node


Receiver Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy
  :noindex:
  :members: create_receiver, update_receiver, delete_receiver,
            get_receiver, find_receiver, receivers


Action Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy
  :noindex:
  :members: get_action, actions


Event Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy
  :noindex:
  :members: get_event, events


Helper Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy
  :noindex:
  :members: wait_for_delete, wait_for_status


Service Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.clustering.v1._proxy.Proxy
  :noindex:
  :members: services
