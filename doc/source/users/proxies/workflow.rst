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

   .. automethod:: openstack.workflow.v2._proxy.Proxy.create_workflow
   .. automethod:: openstack.workflow.v2._proxy.Proxy.delete_workflow
   .. automethod:: openstack.workflow.v2._proxy.Proxy.get_workflow
   .. automethod:: openstack.workflow.v2._proxy.Proxy.find_workflow
   .. automethod:: openstack.workflow.v2._proxy.Proxy.workflows

Execution Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.workflow.v2._proxy.Proxy

   .. automethod:: openstack.workflow.v2._proxy.Proxy.create_execution
   .. automethod:: openstack.workflow.v2._proxy.Proxy.delete_execution
   .. automethod:: openstack.workflow.v2._proxy.Proxy.get_execution
   .. automethod:: openstack.workflow.v2._proxy.Proxy.find_execution
   .. automethod:: openstack.workflow.v2._proxy.Proxy.executions
