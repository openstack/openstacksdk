Placement API
=============

.. automodule:: openstack.placement.v1._proxy

The Placement Class
-------------------

The placement high-level interface is available through the ``placement``
member of a :class:`~openstack.connection.Connection` object.
The ``placement`` member will only be added if the service is detected.

Resource Classes
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.placement.v1._proxy.Proxy
  :noindex:
  :members: create_resource_class, update_resource_class,
            delete_resource_class, get_resource_class,
            resource_classes

Resource Providers
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.placement.v1._proxy.Proxy
  :noindex:
  :members: create_resource_provider, update_resource_provider,
            delete_resource_provider, get_resource_provider,
            find_resource_provider, resource_providers
