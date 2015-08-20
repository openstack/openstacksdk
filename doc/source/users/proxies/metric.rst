Metric API
==========

For details on how to use metric, see :doc:`/users/guides/metric`

.. automodule:: openstack.metric.v1._proxy

The Metric Class
----------------

The metric high-level interface is available through the ``metric`` member of a
:class:`~openstack.connection.Connection` object.  The ``metric`` member will
only be added if the service is detected.

.. autoclass:: openstack.metric.v1._proxy.Proxy
   :members:
