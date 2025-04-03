Compute API
===========

For details on how to use compute, see :doc:`/user/guides/compute`

.. automodule:: openstack.compute.v2._proxy

The Compute Class
-----------------

The compute high-level interface is available through the ``compute``
member of a :class:`~openstack.connection.Connection` object.  The
``compute`` member will only be added if the service is detected.


Server Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: create_server, update_server, delete_server, get_server,
            find_server, servers, get_server_metadata, set_server_metadata,
            delete_server_metadata, wait_for_server, create_server_image,
            backup_server

Network Actions
***************

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: add_fixed_ip_to_server, remove_fixed_ip_from_server,
            add_floating_ip_to_server, remove_floating_ip_from_server,
            fetch_server_security_groups, add_security_group_to_server,
            remove_security_group_from_server

Starting, Stopping, etc.
************************

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: start_server, stop_server, suspend_server, resume_server,
            reboot_server, restore_server, shelve_server, unshelve_server,
            lock_server, unlock_server, pause_server, unpause_server,
            rescue_server, unrescue_server, evacuate_server, migrate_server,
            live_migrate_server

Modifying a Server
******************

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: resize_server, confirm_server_resize, revert_server_resize,
            rebuild_server, reset_server_state, change_server_password,
            get_server_password

Image Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: images, get_image, find_image, delete_image, get_image_metadata,
            set_image_metadata, delete_image_metadata

Flavor Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: create_flavor, delete_flavor, get_flavor, find_flavor, flavors,
            flavor_add_tenant_access, flavor_remove_tenant_access,
            get_flavor_access, fetch_flavor_extra_specs,
            create_flavor_extra_specs, get_flavor_extra_specs_property,
            update_flavor_extra_specs_property,
            delete_flavor_extra_specs_property

Service Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: services, enable_service, disable_service, update_service_forced_down,
            delete_service, update_service, find_service

Volume Attachment Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: create_volume_attachment, update_volume_attachment,
            delete_volume_attachment, get_volume_attachment,
            volume_attachments

Keypair Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: create_keypair, delete_keypair, get_keypair, find_keypair,
            keypairs

Server IPs
^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: server_ips

Server Group Operations
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: create_server_group, delete_server_group, get_server_group,
            find_server_group, server_groups

Server Interface Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: create_server_interface, delete_server_interface,
            get_server_interface, server_interfaces,

Server Tag Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: add_tag_to_server, remove_tag_from_server, remove_tags_from_server

Availability Zone Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: availability_zones

Limits Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: get_limits

Hypervisor Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: get_hypervisor, find_hypervisor, hypervisors,
            get_hypervisor_uptime

Extension Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: find_extension, extensions

QuotaClassSet Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: get_quota_class_set, update_quota_class_set

QuotaSet Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: get_quota_set, get_quota_set_defaults,
            revert_quota_set, update_quota_set

Server Migration Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: abort_server_migration, force_complete_server_migration,
            get_server_migration, server_migrations

Migration Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: migrations

Interactive Consoles
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
  :noindex:
  :members: create_server_remote_console, get_server_console_url,
            validate_console_auth_token, get_server_console_output,
            create_console

Helpers
^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy
   :noindex:
   :members: wait_for_delete
