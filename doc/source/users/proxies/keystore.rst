Keystore API
============

For details on how to use keystore, see :doc:`/users/userguides/keystore`

.. automodule:: openstack.keystore.v1._proxy

The Keystore Class
------------------

The keystore high-level interface is available through the ``keystore``
member of a :class:`~openstack.connection.Connection` object.  The
``keystore`` member will only be added if the service is detected.

.. autoclass:: openstack.keystore.v1._proxy.Proxy
   :members:
