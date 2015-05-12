Volume API
==========

For details on how to use volume, see :doc:`/users/userguides/volume`

.. automodule:: openstack.volume.v2._proxy

The Volume Class
----------------

The volume high-level interface is available through the ``volume`` member of a
:class:`~openstack.connection.Connection` object.  The ``volume`` member will
only be added if the service is detected.

.. autoclass:: openstack.volume.v2._proxy.Proxy
   :members:
