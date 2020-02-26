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

   .. automethod:: openstack.accelerator.v2._proxy.Proxy.get_device
   .. automethod:: openstack.accelerator.v2._proxy.Proxy.devices

Deployable Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.accelerator.v2._proxy.Proxy

   .. automethod:: openstack.accelerator.v2._proxy.Proxy.update_deployable
   .. automethod:: openstack.accelerator.v2._proxy.Proxy.get_deployable
   .. automethod:: openstack.accelerator.v2._proxy.Proxy.deployables

Device Profile Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.accelerator.v2._proxy.Proxy

   .. automethod:: openstack.accelerator.v2._proxy.Proxy.create_device_profile
   .. automethod:: openstack.accelerator.v2._proxy.Proxy.delete_device_profile
   .. automethod:: openstack.accelerator.v2._proxy.Proxy.get_device_profile
   .. automethod:: openstack.accelerator.v2._proxy.Proxy.device_profiles

Accelerator Request Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.accelerator.v2._proxy.Proxy

   .. automethod:: openstack.accelerator.v2._proxy.Proxy.create_accelerator_request
   .. automethod:: openstack.accelerator.v2._proxy.Proxy.delete_accelerator_request
   .. automethod:: openstack.accelerator.v2._proxy.Proxy.get_accelerator_request
   .. automethod:: openstack.accelerator.v2._proxy.Proxy.accelerator_requests
   .. automethod:: openstack.accelerator.v2._proxy.Proxy.update_accelerator_request

