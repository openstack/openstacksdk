Orchestration API
=================

For details on how to use orchestration, see :doc:`/user/guides/orchestration`

.. automodule:: openstack.orchestration.v1._proxy

The Orchestration Class
-----------------------

The orchestration high-level interface is available through the
``orchestration`` member of a :class:`~openstack.connection.Connection`
object.  The ``orchestration`` member will only be added if the service
is detected.

Stack Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.orchestration.v1._proxy.Proxy

   .. automethod:: openstack.orchestration.v1._proxy.Proxy.create_stack
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.check_stack
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.update_stack
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.delete_stack
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.find_stack
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.get_stack
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.get_stack_environment
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.get_stack_files
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.get_stack_template
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.stacks
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.validate_template
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.resources

Software Configuration Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.orchestration.v1._proxy.Proxy

   .. automethod:: openstack.orchestration.v1._proxy.Proxy.create_software_config
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.delete_software_config
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.get_software_config
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.software_configs

Software Deployment Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.orchestration.v1._proxy.Proxy

   .. automethod:: openstack.orchestration.v1._proxy.Proxy.create_software_deployment
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.update_software_deployment
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.delete_software_deployment
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.get_software_deployment
   .. automethod:: openstack.orchestration.v1._proxy.Proxy.software_deployments
