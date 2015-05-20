CDN API
=======

For details on how to use CDN, see :doc:`/users/userguides/cdn`

.. automodule:: openstack.cdn.v1._proxy

The CDN Class
-------------

The CDN high-level interface is available through the ``cdn`` member of a
:class:`~openstack.connection.Connection` object.  The ``cdn`` member will
only be added if the service is detected.

.. autoclass:: openstack.cdn.v1._proxy.Proxy
   :members:
