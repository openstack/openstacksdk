Object Store API
================

For details on how to use this API, see :doc:`/user/guides/object_store`

.. automodule:: openstack.object_store.v1._proxy

The Object Store Class
----------------------

The Object Store high-level interface is exposed as the ``object_store``
object on :class:`~openstack.connection.Connection` objects.

Account Operations
^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.object_store.v1._proxy.Proxy

   .. automethod:: openstack.object_store.v1._proxy.Proxy.get_account_metadata
   .. automethod:: openstack.object_store.v1._proxy.Proxy.set_account_metadata
   .. automethod:: openstack.object_store.v1._proxy.Proxy.delete_account_metadata

Container Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.object_store.v1._proxy.Proxy

   .. automethod:: openstack.object_store.v1._proxy.Proxy.create_container
   .. automethod:: openstack.object_store.v1._proxy.Proxy.delete_container
   .. automethod:: openstack.object_store.v1._proxy.Proxy.containers

   .. automethod:: openstack.object_store.v1._proxy.Proxy.get_container_metadata
   .. automethod:: openstack.object_store.v1._proxy.Proxy.set_container_metadata
   .. automethod:: openstack.object_store.v1._proxy.Proxy.delete_container_metadata

Object Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.object_store.v1._proxy.Proxy

   .. automethod:: openstack.object_store.v1._proxy.Proxy.upload_object
   .. automethod:: openstack.object_store.v1._proxy.Proxy.download_object
   .. automethod:: openstack.object_store.v1._proxy.Proxy.copy_object
   .. automethod:: openstack.object_store.v1._proxy.Proxy.delete_object
   .. automethod:: openstack.object_store.v1._proxy.Proxy.get_object
   .. automethod:: openstack.object_store.v1._proxy.Proxy.objects

   .. automethod:: openstack.object_store.v1._proxy.Proxy.get_object_metadata
   .. automethod:: openstack.object_store.v1._proxy.Proxy.set_object_metadata
   .. automethod:: openstack.object_store.v1._proxy.Proxy.delete_object_metadata
