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
  :members: create_stack, stacks,find_stack, update_stack, delete_stack,
            get_stack, export_stack,
            get_stack_template, get_stack_environment

Stack Resource Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.orchestration.v1._proxy.Proxy
  :noindex:
  :members: resources

Stack Action Operations
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.orchestration.v1._proxy.Proxy
  :noindex:
  :members: suspend_stack, resume_stack, check_stack

Stack Event Operations
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.orchestration.v1._proxy.Proxy
  :noindex:
  :members: stack_events

Stack Template Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.orchestration.v1._proxy.Proxy
  :noindex:
  :members: validate_template

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
