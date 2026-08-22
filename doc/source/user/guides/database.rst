Using OpenStack Database
========================

Before working with the Database service, you'll need to create a connection
to your OpenStack cloud by following the :doc:`connect` user guide. This will
provide you with the ``conn`` variable used in the examples below.

.. contents:: Table of Contents
   :local:

The Database service provisions database instances and manages the databases,
users and flavors associated with them. The examples below show a
representative subset of what is possible; for the complete set of operations,
see the :doc:`Database proxy reference </user/proxies/database>`.

Working with Instances
----------------------

To list the existing database instances, use the
:meth:`~openstack.database.v1._proxy.Proxy.instances` method, which returns a
generator of :class:`~openstack.database.v1.instance.Instance` objects::

    >>> for instance in conn.database.instances():
    ...     print(instance.name, instance.status)

To create an instance, use the
:meth:`~openstack.database.v1._proxy.Proxy.create_instance` method. To retrieve
or delete one, use :meth:`~openstack.database.v1._proxy.Proxy.get_instance` and
:meth:`~openstack.database.v1._proxy.Proxy.delete_instance`::

    >>> instance = conn.database.create_instance(
    ...     name='my-instance', flavor_reference=flavor.id, volume={'size': 5})
    >>> conn.database.delete_instance(instance)

Working with Databases and Users
--------------------------------

Databases and users are created against an existing instance. Use
:meth:`~openstack.database.v1._proxy.Proxy.create_database` and
:meth:`~openstack.database.v1._proxy.Proxy.create_user`, and list them with
:meth:`~openstack.database.v1._proxy.Proxy.databases` and
:meth:`~openstack.database.v1._proxy.Proxy.users`::

    >>> conn.database.create_database(instance, name='my-database')
    >>> conn.database.create_user(
    ...     instance, name='alice', password='s3cret')

Working with Flavors
--------------------

Flavors describe the compute and memory resources of an instance. List the
available flavors with :meth:`~openstack.database.v1._proxy.Proxy.flavors`::

    >>> for flavor in conn.database.flavors():
    ...     print(flavor.name)
