Accelerator API
===============

.. automodule:: openstack.accelerator.v2._proxy

The Accelerator Class
---------------------

The accelerator high-level interface is available through the ``accelerator``
member of a :class:`~openstack.connection.Connection` object.
The ``accelerator`` member will only be added if the service is detected.


Device Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.accelerator.v2._proxy.Proxy
  :noindex:
  :members: devices, get_device

Deployable Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.accelerator.v2._proxy.Proxy
  :noindex:
  :members: deployables, get_deployable, update_deployable

Device Profile Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.accelerator.v2._proxy.Proxy
  :noindex:
  :members: device_profiles, get_device_profile,
            create_device_profile, delete_device_profile

Accelerator Request Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.accelerator.v2._proxy.Proxy
  :noindex:
  :members: accelerator_requests, get_accelerator_request,
            create_accelerator_request, delete_accelerator_request,
            update_accelerator_request
