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
  :noindex:
  :members: create_network, update_network, delete_network, get_network,
            find_network, networks, get_network_ip_availability,
            find_network_ip_availability, network_ip_availabilities,
            add_dhcp_agent_to_network, remove_dhcp_agent_from_network,
            dhcp_agent_hosting_networks,

Port Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_port, create_ports, update_port, delete_port, get_port,
            find_port, ports, add_ip_to_port, remove_ip_from_port

Router Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_router, update_router, delete_router, get_router,
            find_router, routers,
            add_gateway_to_router, remove_gateway_from_router,
            add_interface_to_router, remove_interface_from_router,
            add_extra_routes_to_router, remove_extra_routes_from_router

Floating IP Operations
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_ip, update_ip, delete_ip, get_ip, find_ip,
            find_available_ip, ips

Pool Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_pool, update_pool, delete_pool, get_pool, find_pool, pools,
            create_pool_member, update_pool_member, delete_pool_member,
            get_pool_member, find_pool_member, pool_members

Auto Allocated Topology Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: delete_auto_allocated_topology, get_auto_allocated_topology,
            validate_auto_allocated_topology

Security Group Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_security_group, update_security_group,
            delete_security_group, get_security_group,
            get_security_group_rule, find_security_group,
            find_security_group_rule, security_group_rules,
            security_groups, create_security_group_rule,
            create_security_group_rules, delete_security_group_rule

Availability Zone Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: availability_zones

Address Scope Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_address_scope, update_address_scope, delete_address_scope,
            get_address_scope, find_address_scope, address_scopes

Quota Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: update_quota, delete_quota, get_quota, get_quota_default, quotas

QoS Operations
^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_qos_policy, update_qos_policy, delete_qos_policy,
            get_qos_policy, find_qos_policy, qos_policies, get_qos_rule_type,
            find_qos_rule_type, qos_rule_types,
            create_qos_minimum_bandwidth_rule,
            update_qos_minimum_bandwidth_rule,
            delete_qos_minimum_bandwidth_rule,
            get_qos_minimum_bandwidth_rule,
            find_qos_minimum_bandwidth_rule,
            qos_minimum_bandwidth_rules,
            create_qos_bandwidth_limit_rule,
            update_qos_bandwidth_limit_rule,
            delete_qos_bandwidth_limit_rule,
            get_qos_bandwidth_limit_rule, find_qos_bandwidth_limit_rule,
            qos_bandwidth_limit_rules,
            create_qos_dscp_marking_rule, update_qos_dscp_marking_rule,
            delete_qos_dscp_marking_rule, get_qos_dscp_marking_rule,
            find_qos_dscp_marking_rule, qos_dscp_marking_rules

Agent Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: delete_agent, update_agent, get_agent, agents,
            agent_hosted_routers, routers_hosting_l3_agents,
            network_hosting_dhcp_agents, add_router_to_agent,
            remove_router_from_agent

RBAC Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_rbac_policy, update_rbac_policy, delete_rbac_policy,
            get_rbac_policy, find_rbac_policy, rbac_policies

Listener Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_listener, update_listener, delete_listener,
            get_listener, find_listener, listeners

Subnet Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_subnet, update_subnet, delete_subnet, get_subnet,
            get_subnet_ports, find_subnet, subnets, create_subnet_pool,
            update_subnet_pool, delete_subnet_pool, get_subnet_pool,
            find_subnet_pool, subnet_pools

Load Balancer Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_load_balancer, update_load_balancer, delete_load_balancer,
            get_load_balancer, find_load_balancer, load_balancers

Health Monitor Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_health_monitor, update_health_monitor,
            delete_health_monitor, get_health_monitor, find_health_monitor,
            health_monitors

Metering Label Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_metering_label, update_metering_label,
            delete_metering_label, get_metering_label, find_metering_label,
            metering_labels, create_metering_label_rule,
            update_metering_label_rule, delete_metering_label_rule,
            get_metering_label_rule, find_metering_label_rule,
            metering_label_rules

Segment Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_segment, update_segment, delete_segment, get_segment,
            find_segment, segments

Flavor Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_flavor, update_flavor, delete_flavor, get_flavor,
            find_flavor, flavors

Service Profile Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_service_profile, update_service_profile,
            delete_service_profile, get_service_profile, find_service_profile,
            service_profiles, associate_flavor_with_service_profile,
            disassociate_flavor_from_service_profile

Tag Operations
^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: set_tags

VPN Operations
^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: create_vpn_service, update_vpn_service, delete_vpn_service,
            get_vpn_service, find_vpn_service, vpn_services

Extension Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: find_extension, extensions

Service Provider Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.network.v2._proxy.Proxy
  :noindex:
  :members: service_providers
