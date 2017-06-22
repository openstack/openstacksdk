==========================================
 Using os-client-config in an Application
==========================================

Usage
-----

The simplest and least useful thing you can do is:

.. code-block:: python

  python -m os_client_config.config

Which will print out whatever if finds for your config. If you want to use
it from python, which is much more likely what you want to do, things like:

Get a named cloud.

.. code-block:: python

  import os_client_config

  cloud_config = os_client_config.OpenStackConfig().get_one_cloud(
      'internap', region_name='ams01')
  print(cloud_config.name, cloud_config.region, cloud_config.config)

Or, get all of the clouds.

.. code-block:: python

  import os_client_config

  cloud_config = os_client_config.OpenStackConfig().get_all_clouds()
  for cloud in cloud_config:
      print(cloud.name, cloud.region, cloud.config)

argparse
--------

If you're using os-client-config from a program that wants to process
command line options, there is a registration function to register the
arguments that both os-client-config and keystoneauth know how to deal
with - as well as a consumption argument.

.. code-block:: python

  import argparse
  import sys

  import os_client_config

  cloud_config = os_client_config.OpenStackConfig()
  parser = argparse.ArgumentParser()
  cloud_config.register_argparse_arguments(parser, sys.argv)

  options = parser.parse_args()

  cloud = cloud_config.get_one_cloud(argparse=options)

Constructing OpenStack SDK object
---------------------------------

If what you want to do is get an OpenStack SDK Connection and you want it to
do all the normal things related to clouds.yaml, `OS_` environment variables,
a helper function is provided. The following will get you a fully configured
`openstacksdk` instance.

.. code-block:: python

  import os_client_config

  sdk = os_client_config.make_sdk()

If you want to do the same thing but on a named cloud.

.. code-block:: python

  import os_client_config

  sdk = os_client_config.make_sdk(cloud='mtvexx')

If you want to do the same thing but also support command line parsing.

.. code-block:: python

  import argparse

  import os_client_config

  sdk = os_client_config.make_sdk(options=argparse.ArgumentParser())

It should be noted that OpenStack SDK has ways to construct itself that allow
for additional flexibility. If the helper function here does not meet your
needs, you should see the `from_config` method of
`openstack.connection.Connection <http://developer.openstack.org/sdks/python/openstacksdk/users/guides/connect_from_config.html>`_

Constructing shade objects
--------------------------

If what you want to do is get a
`shade <http://docs.openstack.org/infra/shade/>`_ OpenStackCloud object, a
helper function that honors clouds.yaml and `OS_` environment variables is
provided. The following will get you a fully configured `OpenStackCloud`
instance.

.. code-block:: python

  import os_client_config

  cloud = os_client_config.make_shade()

If you want to do the same thing but on a named cloud.

.. code-block:: python

  import os_client_config

  cloud = os_client_config.make_shade(cloud='mtvexx')

If you want to do the same thing but also support command line parsing.

.. code-block:: python

  import argparse

  import os_client_config

  cloud = os_client_config.make_shade(options=argparse.ArgumentParser())

Constructing REST API Clients
-----------------------------

What if you want to make direct REST calls via a Session interface? You're
in luck. A similar interface is available as with `openstacksdk` and `shade`.
The main difference is that you need to specify which service you want to
talk to and `make_rest_client` will return you a keystoneauth Session object
that is mounted on the endpoint for the service you're looking for.

.. code-block:: python

  import os_client_config

  session = os_client_config.make_rest_client('compute', cloud='vexxhost')

  response = session.get('/servers')
  server_list = response.json()['servers']

Constructing Legacy Client objects
----------------------------------

If you want get an old-style Client object from a python-\*client library,
and you want it to do all the normal things related to clouds.yaml, `OS_`
environment variables, a helper function is also provided. The following
will get you a fully configured `novaclient` instance.

.. code-block:: python

  import os_client_config

  nova = os_client_config.make_client('compute')

If you want to do the same thing but on a named cloud.

.. code-block:: python

  import os_client_config

  nova = os_client_config.make_client('compute', cloud='mtvexx')

If you want to do the same thing but also support command line parsing.

.. code-block:: python

  import argparse

  import os_client_config

  nova = os_client_config.make_client(
      'compute', options=argparse.ArgumentParser())

If you want to get fancier than that in your python, then the rest of the
API is available to you. But often times, you just want to do the one thing.
