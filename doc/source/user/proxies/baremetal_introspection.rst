Baremetal Introspection API
===========================

.. automodule:: openstack.baremetal_introspection.v1._proxy

The Baremetal Introspection Proxy
---------------------------------

The baremetal introspection high-level interface is available through
the ``baremetal_introspection`` member of a
:class:`~openstack.connection.Connection` object.
The ``baremetal_introspection`` member will only be added if the service is
detected.

Introspection Process Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.baremetal_introspection.v1._proxy.Proxy

   .. automethod:: openstack.baremetal_introspection.v1._proxy.Proxy.introspections
   .. automethod:: openstack.baremetal_introspection.v1._proxy.Proxy.get_introspection
   .. automethod:: openstack.baremetal_introspection.v1._proxy.Proxy.get_introspection_data
   .. automethod:: openstack.baremetal_introspection.v1._proxy.Proxy.start_introspection
   .. automethod:: openstack.baremetal_introspection.v1._proxy.Proxy.wait_for_introspection
   .. automethod:: openstack.baremetal_introspection.v1._proxy.Proxy.abort_introspection
