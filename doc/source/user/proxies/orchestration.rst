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
  :noindex:
  :members: create_stack, check_stack, update_stack, delete_stack, find_stack,
            get_stack, get_stack_environment, get_stack_files,
            get_stack_template, stacks, validate_template, resources

Software Configuration Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.orchestration.v1._proxy.Proxy
  :noindex:
  :members: create_software_config, delete_software_config,
            get_software_config, software_configs

Software Deployment Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.orchestration.v1._proxy.Proxy
  :noindex:
  :members: create_software_deployment, update_software_deployment,
            delete_software_deployment, get_software_deployment,
            software_deployments
