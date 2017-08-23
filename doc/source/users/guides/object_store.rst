Using OpenStack Object Store
============================

Before working with the Object Store service, you'll need to create a
connection to your OpenStack cloud by following the :doc:`connect` user
guide. This will provide you with the ``conn`` variable used in the examples
below.

.. contents:: Table of Contents
   :local:

The primary resources of the Object Store service are containers and objects.

Working with Containers
-----------------------

Listing Containers
******************

To list existing containers, use the
:meth:`~openstack.object_store.v1._proxy.Proxy.containers` method. ::

    >>> for cont in conn.object_store.containers():
    ...     print cont
    ...
    openstack.object_store.v1.container.Container: {u'count': 5,
    u'bytes': 500, u'name': u'my container'}
    openstack.object_store.v1.container.Container: {u'count': 0,
    u'bytes': 0, u'name': u'empty container'}
    openstack.object_store.v1.container.Container: {u'count': 100,
    u'bytes': 1000000, u'name': u'another container'}

The ``containers`` method returns a generator which yields
:class:`~openstack.object_store.v1.container.Container` objects. It handles
pagination for you, which can be adjusted via the ``limit`` argument.
By default, the ``containers`` method will yield as many containers as the
service will return, and it will continue requesting until it receives
no more. ::

    >>> for cont in conn.object_store.containers(limit=500):
    ...     print(cont)
    ...
    <500 Containers>
    ... another request transparently made to the Object Store service
    <500 more Containers>
    ...

Creating Containers
*******************

To create a container, use the
:meth:`~openstack.object_store.v1._proxy.Proxy.create_container` method. ::

    >>> cont = conn.object_store.create_container(name="new container")
    >>> cont
    openstack.object_store.v1.container.Container: {'name': u'new container'}

Working with Container Metadata
*******************************

To get the metadata for a container, use the
:meth:`~openstack.object_store.v1._proxy.Proxy.get_container_metadata` method.
This method either takes the name of a container, or a
:class:`~openstack.object_store.v1.container.Container` object, and it returns
a `Container` object with all of its metadata attributes set. ::

    >>> cont = conn.object_store.get_container_metadata("new container")
    openstack.object_store.v1.container.Container: {'content-length': '0',
    'x-container-object-count': '0', 'name': u'new container',
    'accept-ranges': 'bytes',
    'x-trans-id': 'tx22c5de63466e4c05bb104-0054740c39',
    'date': 'Tue, 25 Nov 2014 04:57:29 GMT',
    'x-timestamp': '1416889793.23520', 'x-container-read': '.r:mysite.com',
    'x-container-bytes-used': '0', 'content-type': 'text/plain; charset=utf-8'}

To set the metadata for a container, use the
:meth:`~openstack.object_store.v1._proxy.Proxy.set_container_metadata` method.
This method takes a :class:`~openstack.object_store.v1.container.Container`
object. For example, to grant another user write access to this container,
you can set the
:attr:`~openstack.object_store.v1.container.Container.write_ACL` on a
resource and pass it to `set_container_metadata`. ::

    >>> cont.write_ACL = "big_project:another_user"
    >>> conn.object_store.set_container_metadata(cont)
    openstack.object_store.v1.container.Container: {'content-length': '0',
    'x-container-object-count': '0',
    'name': u'my new container', 'accept-ranges': 'bytes',
    'x-trans-id': 'txc3ee751f971d41de9e9f4-0054740ec1',
    'date': 'Tue, 25 Nov 2014 05:08:17 GMT',
    'x-timestamp': '1416889793.23520', 'x-container-read': '.r:mysite.com',
    'x-container-bytes-used': '0', 'content-type': 'text/plain; charset=utf-8',
    'x-container-write': 'big_project:another_user'}

Working with Objects
--------------------

Objects are held in containers. From an API standpoint, you work with
them using similarly named methods, typically with an additional argument
to specify their container.

Listing Objects
***************

To list the objects that exist in a container, use the
:meth:`~openstack.object_store.v1._proxy.Proxy.objects` method.

If you have a :class:`~openstack.object_store.v1.container.Container`
object, you can pass it to ``objects``. ::

    >>> print cont.name
    pictures
    >>> for obj in conn.object_store.objects(cont):
    ...     print obj
    ...
    openstack.object_store.v1.container.Object:
    {u'hash': u'0522d4ccdf9956badcb15c4087a0c4cb',
    u'name': u'pictures/selfie.jpg', u'bytes': 15744,
    'last-modified': u'2014-10-31T06:33:36.618640',
    u'last_modified': u'2014-10-31T06:33:36.618640',
    u'content_type': u'image/jpeg', 'container': u'pictures',
    'content-type': u'image/jpeg'}
    ...

Similar to the :meth:`~openstack.object_store.v1._proxy.Proxy.containers`
method, ``objects`` returns a generator which yields
:class:`~openstack.object_store.v1.obj.Object` objects stored in the
container. It also handles pagination for you, which you can adjust
with the ``limit`` parameter, otherwise making each request for the maximum
that your Object Store will return.

If you have the name of a container instead of an object, you can also
pass that to the ``objects`` method. ::

    >>> for obj in conn.object_store.objects("pictures".decode("utf8"),
                                             limit=100):
    ...     print obj
    ...
    <100 Objects>
    ... another request transparently made to the Object Store service
    <100 more Objects>

Getting Object Data
*******************

Once you have an :class:`~openstack.object_store.v1.obj.Object`, you get
the data stored inside of it with the
:meth:`~openstack.object_store.v1._proxy.Proxy.get_object_data` method. ::

    >>> print ob.name
    message.txt
    >>> data = conn.object_store.get_object_data(ob)
    >>> print data
    Hello, world!

Additionally, if you want to save the object to disk, the
:meth:`~openstack.object_store.v1._proxy.Proxy.download_object` convenience
method takes an :class:`~openstack.object_store.v1.obj.Object` and a
``path`` to write the contents to. ::

    >>> conn.object_store.download_object(ob, "the_message.txt")

Uploading Objects
*****************

Once you have data you'd like to store in the Object Store service, you use
the :meth:`~openstack.object_store.v1._proxy.Proxy.upload_object` method.
This method takes the ``data`` to be stored, along with at least an object
``name`` and the ``container`` it is to be stored in. ::

    >>> hello = conn.object_store.upload_object(container="messages",
                                                name="helloworld.txt",
                                                data="Hello, world!")
    >>> print hello
    openstack.object_store.v1.container.Object: {'content-length': '0',
    'container': u'messages', 'name': u'helloworld.txt',
    'last-modified': 'Tue, 25 Nov 2014 17:39:29 GMT',
    'etag': '5eb63bbbe01eeed093cb22bb8f5acdc3',
    'x-trans-id': 'tx3035d41b03334aeaaf3dd-005474bed0',
    'date': 'Tue, 25 Nov 2014 17:39:28 GMT',
    'content-type': 'text/html; charset=UTF-8'}

Working with Object Metadata
****************************

Working with metadata on objects is identical to how it's done with
containers. You use the
:meth:`~openstack.object_store.v1._proxy.Proxy.get_object_metadata` and
:meth:`~openstack.object_store.v1._proxy.Proxy.set_object_metadata` methods.

The metadata attributes to be set can be found on the
:class:`~openstack.object_store.v1.obj.Object` object. ::

    >>> secret.delete_after = 300
    >>> secret = conn.object_store.set_object_metadata(secret)

We set the :attr:`~openstack.object_store.obj.Object.delete_after`
value to 500 seconds, causing the object to be deleted in 300 seconds,
or five minutes. That attribute corresponds to the ``X-Delete-After``
header value, which you can see is returned when we retrieve the updated
metadata. ::

    >>> conn.object_store.get_object_metadata(ob)
    openstack.object_store.v1.container.Object: {'content-length': '11',
    'container': u'Secret Container',
    'name': u'selfdestruct.txt', 'x-delete-after': 300,
    'accept-ranges': 'bytes', 'last-modified': 'Tue, 25 Nov 2014 17:50:45 GMT',
    'etag': '5eb63bbbe01eeed093cb22bb8f5acdc3',
    'x-timestamp': '1416937844.36805',
    'x-trans-id': 'tx5c3fd94adf7c4e1b8f334-005474c17b',
    'date': 'Tue, 25 Nov 2014 17:50:51 GMT', 'content-type': 'text/plain'}
