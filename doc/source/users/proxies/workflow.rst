Workflow API
============

For details on how to use block_store, see :doc:`/users/guides/block_store`

.. automodule:: openstack.workflow.v2._proxy

The Workflow Class
------------------

The workflow high-level interface is available through the ``workflow``
member of a :class:`~openstack.connection.Connection` object.
The ``workflow`` member will only be added if the service is detected.

.. autoclass:: openstack.workflow.v2._proxy.Proxy
   :members:
