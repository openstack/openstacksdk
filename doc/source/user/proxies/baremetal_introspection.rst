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
  :noindex:
  :members: introspections, get_introspection, get_introspection_data,
            start_introspection, wait_for_introspection, abort_introspection
