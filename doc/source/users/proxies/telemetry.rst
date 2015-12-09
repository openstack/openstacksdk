Telemetry API
=============

.. caution::
   BETA: This API is a work in progress and is subject to change.

For details on how to use telemetry, see :doc:`/users/guides/telemetry`

.. automodule:: openstack.telemetry.v2._proxy

The Telemetry Class
-------------------

The telemetry high-level interface is available through the ``telemetry``
member of a :class:`~openstack.connection.Connection` object.  The
``telemetry`` member will only be added if the service is detected.

.. autoclass:: openstack.telemetry.v2._proxy.Proxy
   :members:
