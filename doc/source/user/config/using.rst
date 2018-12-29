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

  import openstack

  parser = argparse.ArgumentParser()
  cloud = openstack.connect(options=parser)
