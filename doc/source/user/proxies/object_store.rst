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
  :noindex:
  :members: get_account_metadata, set_account_metadata, delete_account_metadata

Container Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.object_store.v1._proxy.Proxy
  :noindex:
  :members: create_container, delete_container, containers,
            get_container_metadata, set_container_metadata,
            delete_container_metadata

Object Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.object_store.v1._proxy.Proxy
  :noindex:
  :members: upload_object, download_object, copy_object, delete_object,
            get_object, objects, get_object_metadata, set_object_metadata,
            delete_object_metadata
