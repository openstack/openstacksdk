Orchestration API
=================

For details on how to use orchestration, see :doc:`/users/guides/orchestration`

.. automodule:: openstack.orchestration.v1._proxy

The Orchestration Class
-----------------------

The orchestration high-level interface is available through the
``orchestration`` member of a :class:`~openstack.connection.Connection`
object.  The ``orchestration`` member will only be added if the service
is detected.

.. autoclass:: openstack.orchestration.v1._proxy.Proxy
   :members:
