Network API
===========

For details on how to use network, see :doc:`/users/guides/network`

.. automodule:: openstack.network.v2._proxy

The Network Class
-----------------

The network high-level interface is available through the ``network``
member of a :class:`~openstack.connection.Connection` object.  The
``network`` member will only be added if the service is detected.

.. autoclass:: openstack.network.v2._proxy.Proxy
   :members:
