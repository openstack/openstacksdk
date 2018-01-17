Image API v2
============

For details on how to use image, see :doc:`/user/guides/image`

.. automodule:: openstack.image.v2._proxy

The Image v2 Class
------------------

The image high-level interface is available through the ``image`` member of a
:class:`~openstack.connection.Connection` object.  The ``image`` member will
only be added if the service is detected.

Image Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.image.v2._proxy.Proxy

   .. automethod:: openstack.image.v2._proxy.Proxy.upload_image
   .. automethod:: openstack.image.v2._proxy.Proxy.download_image
   .. automethod:: openstack.image.v2._proxy.Proxy.update_image
   .. automethod:: openstack.image.v2._proxy.Proxy.delete_image
   .. automethod:: openstack.image.v2._proxy.Proxy.get_image
   .. automethod:: openstack.image.v2._proxy.Proxy.find_image
   .. automethod:: openstack.image.v2._proxy.Proxy.images
   .. automethod:: openstack.image.v2._proxy.Proxy.deactivate_image
   .. automethod:: openstack.image.v2._proxy.Proxy.reactivate_image
   .. automethod:: openstack.image.v2._proxy.Proxy.add_tag
   .. automethod:: openstack.image.v2._proxy.Proxy.remove_tag

Member Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.image.v2._proxy.Proxy

   .. automethod:: openstack.image.v2._proxy.Proxy.add_member
   .. automethod:: openstack.image.v2._proxy.Proxy.remove_member
   .. automethod:: openstack.image.v2._proxy.Proxy.update_member
   .. automethod:: openstack.image.v2._proxy.Proxy.get_member
   .. automethod:: openstack.image.v2._proxy.Proxy.find_member
   .. automethod:: openstack.image.v2._proxy.Proxy.members
