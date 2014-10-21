Connection
==========
.. automodule:: openstack.connection

Connection Object
-----------------

.. autoclass:: openstack.connection.Connection
   :members:

Examples
--------

At a minimum, the ``Connection`` class needs to be created with an
authenticator or the parameters to build one.

Create a connection
~~~~~~~~~~~~~~~~~~~

The following example constructor uses the identity authenticator using
username and password.  The default settings for the transport are used
by this connection.::

    from openstack import connection
    auth_args = {
        'auth_url': 'http://172.20.1.108:5000/v3',
        'project_name': 'admin',
        'user_name': 'admin',
        'password': 'admin',
    }
    conn = connection.Connection(**auth_args)

List
~~~~

Services are accessed through an attribute named after the service.  A list
of all the projects is retrieved in this manner::

    projects = conn.identity.list_projects()

Find or create
~~~~~~~~~~~~~~

If you wanted to make sure you had a network named 'jenkins', you would first
try to find it and if that fails, you would create it::

    try:
        network = conn.network.find_network("jenkins")
    except exceptions.ResourceNotFound:
        network = conn.network.create_network({"name": "jenkins"})
