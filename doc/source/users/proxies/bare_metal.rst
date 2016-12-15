Bare Metal API
==============

For details on how to use bare_metal, see :doc:`/users/guides/bare_metal`

.. automodule:: openstack.bare_metal.v1._proxy

The BareMetal Class
--------------------

The bare_metal high-level interface is available through the ``bare_metal``
member of a :class:`~openstack.connection.Connection` object.
The ``bare_metal`` member will only be added if the service is detected.

.. autoclass:: openstack.bare_metal.v1._proxy.Proxy
   :members:
