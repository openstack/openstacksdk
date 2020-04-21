Image API v1
============

For details on how to use image, see :doc:`/user/guides/image`

.. automodule:: openstack.image.v1._proxy

The Image v1 Class
------------------

The image high-level interface is available through the ``image`` member of a
:class:`~openstack.connection.Connection` object.  The ``image`` member will
only be added if the service is detected.

.. autoclass:: openstack.image.v1._proxy.Proxy
  :noindex:
  :members: upload_image, update_image, delete_image, get_image, find_image,
            images
