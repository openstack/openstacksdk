Metric API
==========

.. automodule:: openstack.metric.v1._proxy

The Metric Class
----------------

The metric high-level interface is available through the ``metric``
member of a :class:`~openstack.connection.Connection` object.  The
``metric`` member will only be added if the service is detected.

Capability Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.metric.v1._proxy.Proxy

   .. automethod:: openstack.metric.v1._proxy.Proxy.capabilities
