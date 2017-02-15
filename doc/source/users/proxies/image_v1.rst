Image API v1
============

For details on how to use image, see :doc:`/users/guides/image`

.. automodule:: openstack.image.v1._proxy

The Image v1 Class
------------------

The image high-level interface is available through the ``image`` member of a
:class:`~openstack.connection.Connection` object.  The ``image`` member will
only be added if the service is detected.

.. autoclass:: openstack.image.v1._proxy.Proxy

   .. automethod:: openstack.image.v1._proxy.Proxy.upload_image
   .. automethod:: openstack.image.v1._proxy.Proxy.update_image
   .. automethod:: openstack.image.v1._proxy.Proxy.delete_image
   .. automethod:: openstack.image.v1._proxy.Proxy.get_image
   .. automethod:: openstack.image.v1._proxy.Proxy.find_image
   .. automethod:: openstack.image.v1._proxy.Proxy.images
