Transition from Profile
=======================

.. note:: This section describes migrating code from a previous interface of
          python-openstacksdk and can be ignored by people writing new code.

If you have code that currently uses the :class:`~openstack.profile.Profile`
object and/or an ``authenticator`` instance from an object based on
``openstack.auth.base.BaseAuthPlugin``, that code should be updated to use the
:class:`~openstack.config.cloud_region.CloudRegion` object instead.

.. important::

    :class:`~openstack.profile.Profile` is going away. Existing code using it
    should be migrated as soon as possible.

Writing Code that Works with Both
---------------------------------

These examples should all work with both the old and new interface, with one
caveat. With the old interface, the ``CloudConfig`` object comes from the
``os-client-config`` library, and in the new interface that has been moved
into the SDK. In order to write code that works with both the old and new
interfaces, use the following code to import the config namespace:

.. code-block:: python

  try:
      from openstack import config as occ
  except ImportError:
      from os_client_config import config as occ

The examples will assume that the config module has been imported in that
manner.

.. note:: Yes, there is an easier and less verbose way to do all of these.
          These are verbose to handle both the old and new interfaces in the
          same codebase.

Replacing authenticator
-----------------------

There is no direct replacement for ``openstack.auth.base.BaseAuthPlugin``.
``python-openstacksdk`` uses the `keystoneauth`_ library for authentication
and HTTP interactions. `keystoneauth`_ has `auth plugins`_ that can be used
to control how authentication is done. The ``auth_type`` config parameter
can be set to choose the correct authentication method to be used.

Replacing Profile
-----------------

The right way to replace the use of ``openstack.profile.Profile`` depends
a bit on what you're trying to accomplish. Common patterns are listed below,
but in general the approach is either to pass a cloud name to the
`openstack.connection.Connection` constructor, or to construct a
`openstack.config.cloud_region.CloudRegion` object and pass it to the
constructor.

All of the examples on this page assume that you want to support old and
new interfaces simultaneously. There are easier and less verbose versions
of each that are available if you can just make a clean transition.

Getting a Connection to a named cloud from clouds.yaml
------------------------------------------------------

If you want is to construct a `openstack.connection.Connection` based on
parameters configured in a ``clouds.yaml`` file, or from environment variables:

.. code-block:: python

    import openstack.connection

    conn = connection.from_config(cloud_name='name-of-cloud-you-want')

Getting a Connection from python arguments avoiding clouds.yaml
---------------------------------------------------------------

If, on the other hand, you want to construct a
`openstack.connection.Connection`, but are in a context where reading config
from a clouds.yaml file is undesirable, such as inside of a Service:

* create a `openstack.config.loader.OpenStackConfig` object, telling
  it to not load yaml files. Optionally pass an ``app_name`` and
  ``app_version`` which will be added to user-agent strings.
* get a `openstack.config.cloud_region.CloudRegion` object from it
* get a `openstack.connection.Connection`

.. code-block:: python

    try:
        from openstack import config as occ
    except ImportError:
        from os_client_config import config as occ
    from openstack import connection

    loader = occ.OpenStackConfig(
        load_yaml_files=False,
        app_name='spectacular-app',
        app_version='1.0')
    cloud_region = loader.get_one_cloud(
        region_name='my-awesome-region',
        auth_type='password',
        auth=dict(
            auth_url='https://auth.example.com',
            username='amazing-user',
            user_domain_name='example-domain',
            project_name='astounding-project',
            user_project_name='example-domain',
            password='super-secret-password',
        ))
    conn = connection.from_config(cloud_config=cloud_region)

.. note:: app_name and app_version are completely optional, and auth_type
          defaults to 'password'. They are shown here for clarity as to
          where they should go if they want to be set.

Getting a Connection from python arguments and optionally clouds.yaml
---------------------------------------------------------------------

If you want to make a connection from python arguments and want to allow
one of them to optionally be ``cloud`` to allow selection of a named cloud,
it's essentially the same as the previous example, except without
``load_yaml_files=False``.

.. code-block:: python

    try:
        from openstack import config as occ
    except ImportError:
        from os_client_config import config as occ
    from openstack import connection

    loader = occ.OpenStackConfig(
        app_name='spectacular-app',
        app_version='1.0')
    cloud_region = loader.get_one_cloud(
        region_name='my-awesome-region',
        auth_type='password',
        auth=dict(
            auth_url='https://auth.example.com',
            username='amazing-user',
            user_domain_name='example-domain',
            project_name='astounding-project',
            user_project_name='example-domain',
            password='super-secret-password',
          ))
    conn = connection.from_config(cloud_config=cloud_region)

Parameters to get_one_cloud
---------------------------

The most important things to note are:

* ``auth_type`` specifies which kind of authentication plugin to use. It
  controls how authentication is done, as well as what parameters are required.
* ``auth`` is a dictionary containing the parameters needed by the auth plugin.
  The most common information it needs are user, project, domain, auth_url
  and password.
* The rest of the keyword arguments to
  ``openstack.config.loader.OpenStackConfig.get_one_cloud`` are either
  parameters needed by the `keystoneauth Session`_ object, which control how
  HTTP connections are made, or parameters needed by the
  `keystoneauth Adapter`_ object, which control how services are found in the
  Keystone Catalog.

For `keystoneauth Adapter`_ parameters, since there is one
`openstack.connection.Connection` object but many services, per-service
parameters are formed by using the official ``service_type`` of the service
in question. For instance, to override the endpoint for the ``compute``
service, the parameter ``compute_endpoint_override`` would be used.

``region_name`` in ``openstack.profile.Profile`` was a per-service parameter.
This is no longer a valid concept. An `openstack.connection.Connection` is a
connection to a region of a cloud. If you are in an extreme situation where
you have one service in one region and a different service in a different
region, you must use two different `openstack.connection.Connection` objects.

.. note:: service_type, although a parameter for keystoneauth1.adapter.Adapter,
          is not a valid parameter for get_one_cloud. service_type is the key
          by which services are referred, so saying
          'compute_service_type="henry"' doesn't have any meaning.

.. _keystoneauth: https://docs.openstack.org/keystoneauth/latest/
.. _auth plugins: https://docs.openstack.org/keystoneauth/latest/authentication-plugins.html
.. _keystoneauth Adapter: https://docs.openstack.org/keystoneauth/latest/api/keystoneauth1.html#keystoneauth1.adapter.Adapter
.. _keystoneauth Session: https://docs.openstack.org/keystoneauth/latest/api/keystoneauth1.html#keystoneauth1.session.Session
