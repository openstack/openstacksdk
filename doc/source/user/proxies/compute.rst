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

   .. automethod:: openstack.compute.v2._proxy.Proxy.create_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.update_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.delete_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.get_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.find_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.servers
   .. automethod:: openstack.compute.v2._proxy.Proxy.get_server_metadata
   .. automethod:: openstack.compute.v2._proxy.Proxy.set_server_metadata
   .. automethod:: openstack.compute.v2._proxy.Proxy.delete_server_metadata
   .. automethod:: openstack.compute.v2._proxy.Proxy.wait_for_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.create_server_image
   .. automethod:: openstack.compute.v2._proxy.Proxy.backup_server

Network Actions
***************

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.add_fixed_ip_to_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.remove_fixed_ip_from_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.add_floating_ip_to_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.remove_floating_ip_from_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.add_security_group_to_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.remove_security_group_from_server

Starting, Stopping, etc.
************************

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.start_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.stop_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.suspend_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.resume_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.reboot_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.shelve_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.unshelve_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.lock_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.unlock_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.pause_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.unpause_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.rescue_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.unrescue_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.evacuate_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.migrate_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.get_server_console_output
   .. automethod:: openstack.compute.v2._proxy.Proxy.live_migrate_server

Modifying a Server
******************

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.resize_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.confirm_server_resize
   .. automethod:: openstack.compute.v2._proxy.Proxy.revert_server_resize
   .. automethod:: openstack.compute.v2._proxy.Proxy.rebuild_server
   .. automethod:: openstack.compute.v2._proxy.Proxy.reset_server_state
   .. automethod:: openstack.compute.v2._proxy.Proxy.change_server_password
   .. automethod:: openstack.compute.v2._proxy.Proxy.get_server_password

Image Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.images
   .. automethod:: openstack.compute.v2._proxy.Proxy.get_image
   .. automethod:: openstack.compute.v2._proxy.Proxy.find_image
   .. automethod:: openstack.compute.v2._proxy.Proxy.delete_image
   .. automethod:: openstack.compute.v2._proxy.Proxy.get_image_metadata
   .. automethod:: openstack.compute.v2._proxy.Proxy.set_image_metadata
   .. automethod:: openstack.compute.v2._proxy.Proxy.delete_image_metadata

Flavor Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.create_flavor
   .. automethod:: openstack.compute.v2._proxy.Proxy.delete_flavor
   .. automethod:: openstack.compute.v2._proxy.Proxy.get_flavor
   .. automethod:: openstack.compute.v2._proxy.Proxy.find_flavor
   .. automethod:: openstack.compute.v2._proxy.Proxy.flavors

Service Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.services
   .. automethod:: openstack.compute.v2._proxy.Proxy.enable_service
   .. automethod:: openstack.compute.v2._proxy.Proxy.disable_service
   .. automethod:: openstack.compute.v2._proxy.Proxy.force_service_down

Volume Attachment Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.create_volume_attachment
   .. automethod:: openstack.compute.v2._proxy.Proxy.update_volume_attachment
   .. automethod:: openstack.compute.v2._proxy.Proxy.delete_volume_attachment
   .. automethod:: openstack.compute.v2._proxy.Proxy.get_volume_attachment
   .. automethod:: openstack.compute.v2._proxy.Proxy.volume_attachments

Keypair Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.create_keypair
   .. automethod:: openstack.compute.v2._proxy.Proxy.delete_keypair
   .. automethod:: openstack.compute.v2._proxy.Proxy.get_keypair
   .. automethod:: openstack.compute.v2._proxy.Proxy.find_keypair
   .. automethod:: openstack.compute.v2._proxy.Proxy.keypairs

Server IPs
^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.server_ips

Server Group Operations
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.create_server_group
   .. automethod:: openstack.compute.v2._proxy.Proxy.delete_server_group
   .. automethod:: openstack.compute.v2._proxy.Proxy.get_server_group
   .. automethod:: openstack.compute.v2._proxy.Proxy.find_server_group
   .. automethod:: openstack.compute.v2._proxy.Proxy.server_groups

Server Interface Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.create_server_interface
   .. automethod:: openstack.compute.v2._proxy.Proxy.delete_server_interface
   .. automethod:: openstack.compute.v2._proxy.Proxy.get_server_interface
   .. automethod:: openstack.compute.v2._proxy.Proxy.server_interfaces

Availability Zone Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.availability_zones

Limits Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.get_limits

Hypervisor Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.get_hypervisor
   .. automethod:: openstack.compute.v2._proxy.Proxy.find_hypervisor
   .. automethod:: openstack.compute.v2._proxy.Proxy.hypervisors

Extension Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.compute.v2._proxy.Proxy

   .. automethod:: openstack.compute.v2._proxy.Proxy.find_extension
   .. automethod:: openstack.compute.v2._proxy.Proxy.extensions
