Identity API v3
===============

For details on how to use identity, see :doc:`/user/guides/identity`

.. automodule:: openstack.identity.v3._proxy

The Identity v3 Class
---------------------

The identity high-level interface is available through the ``identity``
member of a :class:`~openstack.connection.Connection` object.  The
``identity`` member will only be added if the service is detected.

Credential Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_credential, update_credential, delete_credential,
            get_credential, find_credential, credentials

Domain Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_domain, update_domain, delete_domain, get_domain,
            find_domain, domains

Domain Config Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_domain_config, delete_domain_config, get_domain_config,
            update_domain_config

Endpoint Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_endpoint, update_endpoint, delete_endpoint, get_endpoint,
            find_endpoint, endpoints, project_endpoints,
            associate_endpoint_with_project, disassociate_endpoint_from_project

Group Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_group, update_group, delete_group, get_group, find_group,
            groups, add_user_to_group, remove_user_from_group,
            check_user_in_group, group_users

Policy Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_policy, update_policy, delete_policy, get_policy,
            find_policy, policies

Project Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_project, update_project, delete_project, get_project,
            find_project, projects, user_projects, endpoint_projects

Service Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_service, update_service, delete_service, get_service,
            find_service, services

User Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_user, update_user, delete_user, get_user, find_user, users,
            user_groups

Trust Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_trust, delete_trust, get_trust, find_trust, trusts

Region Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_region, update_region, delete_region, get_region,
            find_region, regions

Role Operations
^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_role, update_role, delete_role, get_role, find_role, roles

Role Assignment Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: role_assignments, role_assignments_filter,
            assign_project_role_to_user, unassign_project_role_from_user,
            validate_user_has_project_role, assign_project_role_to_group,
            unassign_project_role_from_group, validate_group_has_project_role,
            assign_domain_role_to_user, unassign_domain_role_from_user,
            validate_user_has_domain_role, assign_domain_role_to_group,
            unassign_domain_role_from_group, validate_group_has_domain_role,
            assign_system_role_to_user, unassign_system_role_from_user,
            validate_user_has_system_role, assign_system_role_to_group,
            unassign_system_role_from_group, validate_group_has_system_role

Registered Limit Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: registered_limits, get_registered_limit, create_registered_limit,
            update_registered_limit, delete_registered_limit

Limit Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: limits, get_limit, create_limit, update_limit, delete_limit

Application Credential Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: application_credentials, get_application_credential,
            create_application_credential, find_application_credential,
            delete_application_credential

Federation Protocol Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_federation_protocol, delete_federation_protocol,
            find_federation_protocol, get_federation_protocol,
            federation_protocols, update_federation_protocol

Mapping Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_mapping, delete_mapping, find_mapping, get_mapping,
            mappings, update_mapping

Identity Provider Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_identity_provider, delete_identity_provider,
            find_identity_provider, get_identity_provider, identity_providers,
            update_identity_provider

Access Rule Operations
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: access_rules, access_rules, delete_access_rule

Service Provider Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.identity.v3._proxy.Proxy
  :noindex:
  :members: create_service_provider, delete_service_provider,
            find_service_provider, get_service_provider, service_providers,
            update_service_provider
