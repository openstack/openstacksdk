Connect
=======

In order to work with an OpenStack cloud you first need to create a
:class:`~openstack.connection.Connection` to it using your credentials. A
connection can be created in a number of ways: using a configuration file,
environment variables, or explicit keyword arguments, as illustrated below.

It is recommended to use :ref:`config-clouds-yaml` as the same configuration
file can be shared across tools and languages. For a comprehensive overview of
configuration handling in openstacksdk, see the :doc:`/user/config/index`
guide.

Create a connection via a configuration file
--------------------------------------------

To create a connection via a configuration file, you need a YAML file called
``clouds.yaml``. A simple ``clouds.yaml`` file looks like the following:

.. code-block:: yaml

   clouds:
     mycloud:
       auth:
         auth_url: https://identity.example.com/v3
         username: "my-username"
         password: "secret-password"
         project_name: "my-project"
         user_domain_name: "Default"
         project_domain_name: "Default"
       region_name: "RegionOne"

To create a :class:`~openstack.connection.Connection` instance using this file,
use the :func:`~openstack.connect` factory function and pass the name of the
cloud configuration:

.. literalinclude:: ../examples/connect.py
   :pyobject: create_connection_from_config

For more details on the format of ``clouds.yaml``, including standard file
locations and profile inheritance, refer to :ref:`config-clouds-yaml`.

Command-line options (argparse)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are writing a command-line application, :func:`~openstack.connect` can
integrate directly with Python's standard :mod:`argparse` library.

When you pass an :class:`argparse.ArgumentParser` instance via the ``options``
parameter, openstacksdk registers its standard options (such as ``--os-cloud``)
along with all `keystoneauth`_ authentication and session options (such as
``--os-auth-url``, ``--os-username``, and ``--insecure``). It then parses
``sys.argv`` to configure the connection. This allows your application to
define its own CLI arguments on the parser while letting openstacksdk handle
all OpenStack configuration flags:

.. literalinclude:: ../examples/connect.py
   :pyobject: create_connection_from_args

.. _keystoneauth: https://docs.openstack.org/keystoneauth/latest/

Create a connection via environment variables
---------------------------------------------

You can also build a connection from ``OS_``-prefixed environment variables. If
you have the standard OpenStack environment variables set - for example, by
sourcing an ``openrc`` file - you can create a connection without any
additional configuration:

.. code-block:: python

    import openstack

    conn = openstack.connect()

When no cloud name is given, :func:`~openstack.connect` loads its configuration
from the environment. For the full list of supported environment variables,
refer to :ref:`config-environment-variables`.

Create a connection via explicit arguments
------------------------------------------

To create a :class:`~openstack.connection.Connection` instance via explicit
keyword arguments, pass the connection parameters directly to
:func:`~openstack.connect`:

.. literalinclude:: ../examples/connect.py
   :pyobject: create_connection

.. note:: To enable logging, see the :doc:`logging` user guide.

Next
----
Now that you can create a connection, continue with the :ref:`user_guides`
to work with an OpenStack service.
