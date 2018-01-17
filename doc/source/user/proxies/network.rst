Network API
===========

For details on how to use network, see :doc:`/user/guides/network`

.. automodule:: openstack.network.v2._proxy

The Network Class
-----------------

The network high-level interface is available through the ``network``
member of a :class:`~openstack.connection.Connection` object.  The
``network`` member will only be added if the service is detected.

Network Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_network
   .. automethod:: openstack.network.v2._proxy.Proxy.update_network
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_network
   .. automethod:: openstack.network.v2._proxy.Proxy.get_network
   .. automethod:: openstack.network.v2._proxy.Proxy.find_network
   .. automethod:: openstack.network.v2._proxy.Proxy.networks

   .. automethod:: openstack.network.v2._proxy.Proxy.get_network_ip_availability
   .. automethod:: openstack.network.v2._proxy.Proxy.find_network_ip_availability
   .. automethod:: openstack.network.v2._proxy.Proxy.network_ip_availabilities

   .. automethod:: openstack.network.v2._proxy.Proxy.add_dhcp_agent_to_network
   .. automethod:: openstack.network.v2._proxy.Proxy.remove_dhcp_agent_from_network
   .. automethod:: openstack.network.v2._proxy.Proxy.dhcp_agent_hosting_networks

Port Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_port
   .. automethod:: openstack.network.v2._proxy.Proxy.update_port
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_port
   .. automethod:: openstack.network.v2._proxy.Proxy.get_port
   .. automethod:: openstack.network.v2._proxy.Proxy.find_port
   .. automethod:: openstack.network.v2._proxy.Proxy.ports

   .. automethod:: openstack.network.v2._proxy.Proxy.add_ip_to_port
   .. automethod:: openstack.network.v2._proxy.Proxy.remove_ip_from_port

Router Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_router
   .. automethod:: openstack.network.v2._proxy.Proxy.update_router
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_router
   .. automethod:: openstack.network.v2._proxy.Proxy.get_router
   .. automethod:: openstack.network.v2._proxy.Proxy.find_router
   .. automethod:: openstack.network.v2._proxy.Proxy.routers

   .. automethod:: openstack.network.v2._proxy.Proxy.add_gateway_to_router
   .. automethod:: openstack.network.v2._proxy.Proxy.remove_gateway_from_router
   .. automethod:: openstack.network.v2._proxy.Proxy.add_interface_to_router
   .. automethod:: openstack.network.v2._proxy.Proxy.remove_interface_from_router

Floating IP Operations
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_ip
   .. automethod:: openstack.network.v2._proxy.Proxy.update_ip
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_ip
   .. automethod:: openstack.network.v2._proxy.Proxy.get_ip
   .. automethod:: openstack.network.v2._proxy.Proxy.find_ip
   .. automethod:: openstack.network.v2._proxy.Proxy.find_available_ip
   .. automethod:: openstack.network.v2._proxy.Proxy.ips

Pool Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_pool
   .. automethod:: openstack.network.v2._proxy.Proxy.update_pool
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_pool
   .. automethod:: openstack.network.v2._proxy.Proxy.get_pool
   .. automethod:: openstack.network.v2._proxy.Proxy.find_pool
   .. automethod:: openstack.network.v2._proxy.Proxy.pools

   .. automethod:: openstack.network.v2._proxy.Proxy.create_pool_member
   .. automethod:: openstack.network.v2._proxy.Proxy.update_pool_member
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_pool_member
   .. automethod:: openstack.network.v2._proxy.Proxy.get_pool_member
   .. automethod:: openstack.network.v2._proxy.Proxy.find_pool_member
   .. automethod:: openstack.network.v2._proxy.Proxy.pool_members

Auto Allocated Topology Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.delete_auto_allocated_topology
   .. automethod:: openstack.network.v2._proxy.Proxy.get_auto_allocated_topology
   .. automethod:: openstack.network.v2._proxy.Proxy.validate_auto_allocated_topology

Security Group Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_security_group
   .. automethod:: openstack.network.v2._proxy.Proxy.update_security_group
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_security_group
   .. automethod:: openstack.network.v2._proxy.Proxy.get_security_group
   .. automethod:: openstack.network.v2._proxy.Proxy.get_security_group_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.find_security_group
   .. automethod:: openstack.network.v2._proxy.Proxy.find_security_group_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.security_group_rules
   .. automethod:: openstack.network.v2._proxy.Proxy.security_groups

   .. automethod:: openstack.network.v2._proxy.Proxy.security_group_allow_ping
   .. automethod:: openstack.network.v2._proxy.Proxy.security_group_open_port

   .. automethod:: openstack.network.v2._proxy.Proxy.create_security_group_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_security_group_rule

Availability Zone Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.availability_zones

Address Scope Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_address_scope
   .. automethod:: openstack.network.v2._proxy.Proxy.update_address_scope
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_address_scope
   .. automethod:: openstack.network.v2._proxy.Proxy.get_address_scope
   .. automethod:: openstack.network.v2._proxy.Proxy.find_address_scope
   .. automethod:: openstack.network.v2._proxy.Proxy.address_scopes

Quota Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.update_quota
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_quota
   .. automethod:: openstack.network.v2._proxy.Proxy.get_quota
   .. automethod:: openstack.network.v2._proxy.Proxy.get_quota_default
   .. automethod:: openstack.network.v2._proxy.Proxy.quotas

QoS Operations
^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_qos_policy
   .. automethod:: openstack.network.v2._proxy.Proxy.update_qos_policy
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_qos_policy
   .. automethod:: openstack.network.v2._proxy.Proxy.get_qos_policy
   .. automethod:: openstack.network.v2._proxy.Proxy.find_qos_policy
   .. automethod:: openstack.network.v2._proxy.Proxy.qos_policies
   .. automethod:: openstack.network.v2._proxy.Proxy.get_qos_rule_type
   .. automethod:: openstack.network.v2._proxy.Proxy.find_qos_rule_type
   .. automethod:: openstack.network.v2._proxy.Proxy.qos_rule_types

   .. automethod:: openstack.network.v2._proxy.Proxy.create_qos_minimum_bandwidth_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.update_qos_minimum_bandwidth_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_qos_minimum_bandwidth_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.get_qos_minimum_bandwidth_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.find_qos_minimum_bandwidth_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.qos_minimum_bandwidth_rules

   .. automethod:: openstack.network.v2._proxy.Proxy.create_qos_bandwidth_limit_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.update_qos_bandwidth_limit_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_qos_bandwidth_limit_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.get_qos_bandwidth_limit_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.find_qos_bandwidth_limit_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.qos_bandwidth_limit_rules

   .. automethod:: openstack.network.v2._proxy.Proxy.create_qos_dscp_marking_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.update_qos_dscp_marking_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_qos_dscp_marking_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.get_qos_dscp_marking_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.find_qos_dscp_marking_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.qos_dscp_marking_rules

Agent Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.delete_agent
   .. automethod:: openstack.network.v2._proxy.Proxy.update_agent
   .. automethod:: openstack.network.v2._proxy.Proxy.get_agent
   .. automethod:: openstack.network.v2._proxy.Proxy.agents
   .. automethod:: openstack.network.v2._proxy.Proxy.agent_hosted_routers
   .. automethod:: openstack.network.v2._proxy.Proxy.routers_hosting_l3_agents
   .. automethod:: openstack.network.v2._proxy.Proxy.network_hosting_dhcp_agents

   .. automethod:: openstack.network.v2._proxy.Proxy.add_router_to_agent
   .. automethod:: openstack.network.v2._proxy.Proxy.remove_router_from_agent

RBAC Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_rbac_policy
   .. automethod:: openstack.network.v2._proxy.Proxy.update_rbac_policy
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_rbac_policy
   .. automethod:: openstack.network.v2._proxy.Proxy.get_rbac_policy
   .. automethod:: openstack.network.v2._proxy.Proxy.find_rbac_policy
   .. automethod:: openstack.network.v2._proxy.Proxy.rbac_policies

Listener Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_listener
   .. automethod:: openstack.network.v2._proxy.Proxy.update_listener
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_listener
   .. automethod:: openstack.network.v2._proxy.Proxy.get_listener
   .. automethod:: openstack.network.v2._proxy.Proxy.find_listener
   .. automethod:: openstack.network.v2._proxy.Proxy.listeners

Subnet Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_subnet
   .. automethod:: openstack.network.v2._proxy.Proxy.update_subnet
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_subnet
   .. automethod:: openstack.network.v2._proxy.Proxy.get_subnet
   .. automethod:: openstack.network.v2._proxy.Proxy.get_subnet_ports
   .. automethod:: openstack.network.v2._proxy.Proxy.find_subnet
   .. automethod:: openstack.network.v2._proxy.Proxy.subnets

   .. automethod:: openstack.network.v2._proxy.Proxy.create_subnet_pool
   .. automethod:: openstack.network.v2._proxy.Proxy.update_subnet_pool
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_subnet_pool
   .. automethod:: openstack.network.v2._proxy.Proxy.get_subnet_pool
   .. automethod:: openstack.network.v2._proxy.Proxy.find_subnet_pool
   .. automethod:: openstack.network.v2._proxy.Proxy.subnet_pools

Load Balancer Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_load_balancer
   .. automethod:: openstack.network.v2._proxy.Proxy.update_load_balancer
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_load_balancer
   .. automethod:: openstack.network.v2._proxy.Proxy.get_load_balancer
   .. automethod:: openstack.network.v2._proxy.Proxy.find_load_balancer
   .. automethod:: openstack.network.v2._proxy.Proxy.load_balancers

Health Monitor Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_health_monitor
   .. automethod:: openstack.network.v2._proxy.Proxy.update_health_monitor
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_health_monitor
   .. automethod:: openstack.network.v2._proxy.Proxy.get_health_monitor
   .. automethod:: openstack.network.v2._proxy.Proxy.find_health_monitor
   .. automethod:: openstack.network.v2._proxy.Proxy.health_monitors

Metering Label Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_metering_label
   .. automethod:: openstack.network.v2._proxy.Proxy.update_metering_label
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_metering_label
   .. automethod:: openstack.network.v2._proxy.Proxy.get_metering_label
   .. automethod:: openstack.network.v2._proxy.Proxy.find_metering_label
   .. automethod:: openstack.network.v2._proxy.Proxy.metering_labels

   .. automethod:: openstack.network.v2._proxy.Proxy.create_metering_label_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.update_metering_label_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_metering_label_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.get_metering_label_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.find_metering_label_rule
   .. automethod:: openstack.network.v2._proxy.Proxy.metering_label_rules

Segment Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_segment
   .. automethod:: openstack.network.v2._proxy.Proxy.update_segment
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_segment
   .. automethod:: openstack.network.v2._proxy.Proxy.get_segment
   .. automethod:: openstack.network.v2._proxy.Proxy.find_segment
   .. automethod:: openstack.network.v2._proxy.Proxy.segments

Flavor Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_flavor
   .. automethod:: openstack.network.v2._proxy.Proxy.update_flavor
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_flavor
   .. automethod:: openstack.network.v2._proxy.Proxy.get_flavor
   .. automethod:: openstack.network.v2._proxy.Proxy.find_flavor
   .. automethod:: openstack.network.v2._proxy.Proxy.flavors

Service Profile Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_service_profile
   .. automethod:: openstack.network.v2._proxy.Proxy.update_service_profile
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_service_profile
   .. automethod:: openstack.network.v2._proxy.Proxy.get_service_profile
   .. automethod:: openstack.network.v2._proxy.Proxy.find_service_profile
   .. automethod:: openstack.network.v2._proxy.Proxy.service_profiles

   .. automethod:: openstack.network.v2._proxy.Proxy.associate_flavor_with_service_profile
   .. automethod:: openstack.network.v2._proxy.Proxy.disassociate_flavor_from_service_profile

Tag Operations
^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.set_tags

VPN Operations
^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.create_vpn_service
   .. automethod:: openstack.network.v2._proxy.Proxy.update_vpn_service
   .. automethod:: openstack.network.v2._proxy.Proxy.delete_vpn_service
   .. automethod:: openstack.network.v2._proxy.Proxy.get_vpn_service
   .. automethod:: openstack.network.v2._proxy.Proxy.find_vpn_service
   .. automethod:: openstack.network.v2._proxy.Proxy.vpn_services

Extension Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.find_extension
   .. automethod:: openstack.network.v2._proxy.Proxy.extensions

Service Provider Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy

   .. automethod:: openstack.network.v2._proxy.Proxy.service_providers
