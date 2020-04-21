Workflow API
============

.. automodule:: openstack.workflow.v2._proxy

The Workflow Class
------------------

The workflow high-level interface is available through the ``workflow``
member of a :class:`~openstack.connection.Connection` object.
The ``workflow`` member will only be added if the service is detected.

Workflow Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.workflow.v2._proxy.Proxy
  :noindex:
  :members: create_workflow, delete_workflow, get_workflow,
            find_workflow, workflows

Execution Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.workflow.v2._proxy.Proxy
  :noindex:
  :members: create_execution, delete_execution, get_execution,
            find_execution, executions
