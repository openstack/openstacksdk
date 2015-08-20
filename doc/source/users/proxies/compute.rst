Compute API
===========

For details on how to use compute, see :doc:`/users/guides/compute`

.. automodule:: openstack.compute.v2._proxy

The Compute Class
-----------------

The compute high-level interface is available through the ``compute``
member of a :class:`~openstack.connection.Connection` object.  The
``compute`` member will only be added if the service is detected.

.. autoclass:: openstack.compute.v2._proxy.Proxy
   :members:
