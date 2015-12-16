Using OpenStack Image
=====================

Before working with the Image service, you'll need to create a connection
to your OpenStack cloud by following the :doc:`connect` user guide. This will
provide you with the ``conn`` variable used in the examples below.

The primary resource of the Image service is the image.

List Images
-----------

An **image** is a collection of files for a specific operating system
that you use to create or rebuild a server. OpenStack provides
`pre-built images <http://docs.openstack.org/image-guide/obtain-images.html>`_.
You can also create custom images, or snapshots, from servers that you have
launched. Images come in different formats and are sometimes called virtual
machine images.

.. literalinclude:: ../examples/image/list.py
   :pyobject: list_images

Full example: `image resource list`_

Create Image
------------

Create an image by uploading its data and setting its attributes.

.. literalinclude:: ../examples/image/create.py
   :pyobject: upload_image

Full example: `image resource create`_

Delete Image
------------

Delete an image.

.. literalinclude:: ../examples/image/delete.py
   :pyobject: delete_image

Full example: `image resource delete`_

.. _image resource create: http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/examples/image/create.py
.. _image resource delete: http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/examples/image/delete.py
.. _image resource list: http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/examples/image/list.py
