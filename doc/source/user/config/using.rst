========================================
Using openstack.config in an Application
========================================

Usage
-----

The simplest and least useful thing you can do is:

.. code-block:: python

  python -m openstack.config.loader

Which will print out whatever if finds for your config. If you want to use
it from python, which is much more likely what you want to do, things like:

Get a named cloud.

.. code-block:: python

  import openstack.config

  cloud_region = openstack.config.OpenStackConfig().get_one(
      'internap', region_name='ams01')
  print(cloud_region.name, cloud_region.region, cloud_region.config)

Or, get all of the clouds.

.. code-block:: python

  import openstack.config

  cloud_regions = openstack.config.OpenStackConfig().get_all()
  for cloud_region in cloud_regions:
      print(cloud_region.name, cloud_region.region, cloud_region.config)

argparse
--------

If you're using `openstack.config` from a program that wants to process
command line options, there is a registration function to register the
arguments that both `openstack.config` and keystoneauth know how to deal
with - as well as a consumption argument.

.. code-block:: python

  import argparse
  import sys

  import openstack.config

  config = openstack.config.OpenStackConfig()
  parser = argparse.ArgumentParser()
  config.register_argparse_arguments(parser, sys.argv)

  options = parser.parse_args()

  cloud_region = config.get_one(argparse=options)

Constructing a Connection object
--------------------------------

If what you want to do is get an `openstack.connection.Connection` and you
want it to do all the normal things related to clouds.yaml, `OS_` environment
variables, a helper function is provided. The following will get you a fully
configured `openstacksdk` instance.

.. code-block:: python

  import openstack.config

  conn = openstack.config.make_connection()

If you want to do the same thing but on a named cloud.

.. code-block:: python

  import openstack.config

  conn = openstack.config.make_connection(cloud='mtvexx')

If you want to do the same thing but also support command line parsing.

.. code-block:: python

  import argparse

  import openstack.config

  conn = openstack.config.make_connection(options=argparse.ArgumentParser())

Constructing OpenStackCloud objects
-----------------------------------

If what you want to do is get an
`opentack.cloud.openstackcloud.OpenStackCloud` object, a
helper function that honors clouds.yaml and `OS_` environment variables is
provided. The following will get you a fully configured `OpenStackCloud`
instance.

.. code-block:: python

  import openstack.config

  cloud = openstack.config.make_cloud()

If you want to do the same thing but on a named cloud.

.. code-block:: python

  import openstack.config

  cloud = openstack.config.make_cloud(cloud='mtvexx')

If you want to do the same thing but also support command line parsing.

.. code-block:: python

  import argparse

  import openstack.config

  cloud = openstack.config.make_cloud(options=argparse.ArgumentParser())

Constructing REST API Clients
-----------------------------

What if you want to make direct REST calls via a Session interface? You're
in luck. A similar interface is available as with `openstacksdk` and `shade`.
The main difference is that you need to specify which service you want to
talk to and `make_rest_client` will return you a keystoneauth Session object
that is mounted on the endpoint for the service you're looking for.

.. code-block:: python

  import openstack.config

  session = openstack.config.make_rest_client('compute', cloud='vexxhost')

  response = session.get('/servers')
  server_list = response.json()['servers']
