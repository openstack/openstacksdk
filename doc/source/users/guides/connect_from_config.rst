Connect From Config
===================

In order to work with an OpenStack cloud you first need to create a
:class:`~openstack.connection.Connection` to it using your credentials. A
:class:`~openstack.connection.Connection` can be
created in 3 ways, using the class itself (see :doc:`connect`), a file, or
environment variables as illustrated below. The SDK uses
`os-client-config <http://git.openstack.org/cgit/openstack/os-client-config/tree/README.rst>`_
to handle the configuration.

.. note:: To get your credentials
   `Download the OpenStack RC file <http://docs.openstack.org/cli-reference/common/cli_set_environment_variables_using_openstack_rc.html#download-and-source-the-openstack-rc-file>`_.

Create Connection From A File
-----------------------------

Default Location
****************

To create a connection from a file you need a YAML file to contain the
configuration.

.. literalinclude:: ../../contributors/clouds.yaml
   :language: yaml

To use a configuration file called ``clouds.yaml`` in one of the default
locations:

* Current Directory
* ~/.config/openstack
* /etc/openstack

call :py:func:`~openstack.connection.from_config`. The ``from_config``
function takes three optional arguments:

* **cloud_name** allows you to specify a cloud from your ``clouds.yaml`` file.
* **cloud_config** allows you to pass in an existing
  ``os_client_config.config.OpenStackConfig``` object.
* **options** allows you to specify a namespace object with options to be
  added to the cloud config.

.. literalinclude:: ../examples/connect.py
   :pyobject: Opts

.. literalinclude:: ../examples/connect.py
   :pyobject: create_connection_from_config

.. literalinclude:: ../examples/connect.py
   :pyobject: create_connection_from_args

.. note:: To enable logging, set ``debug=True`` in the ``options`` object.

User Defined Location
*********************

To use a configuration file in a user defined location set the
environment variable ``OS_CLIENT_CONFIG_FILE`` to the
absolute path of a file.::

    export OS_CLIENT_CONFIG_FILE=/path/to/my/config/my-clouds.yaml

and call :py:func:`~openstack.connection.from_config` with the **cloud_name**
of the cloud configuration to use, .

.. Create Connection From Environment Variables
   --------------------------------------------

   TODO(etoews): Document when https://bugs.launchpad.net/os-client-config/+bug/1489617
   is fixed.

Next
----
Now that you can create a connection, continue with the :ref:`user_guides`
for an OpenStack service.
