================
os-client-config
================

`os-client-config` is a library for collecting client configuration for
using an OpenStack cloud in a consistent and comprehensive manner. It
will find cloud config for as few as 1 cloud and as many as you want to
put in a config file. It will read environment variables and config files,
and it also contains some vendor specific default values so that you don't
have to know extra info to use OpenStack

* If you have a config file, you will get the clouds listed in it
* If you have environment variables, you will get a cloud named `envvars`
* If you have neither, you will get a cloud named `defaults` with base defaults

Environment Variables
---------------------

`os-client-config` honors all of the normal `OS_*` variables. It does not
provide backwards compatibility to service-specific variables such as
`NOVA_USERNAME`.

If you have OpenStack environment variables set, `os-client-config` will produce
a cloud config object named `envvars` containing your values from the
environment. If you don't like the name `envvars`, that's ok, you can override
it by setting `OS_CLOUD_NAME`.

Service specific settings, like the nova service type, are set with the
default service type as a prefix. For instance, to set a special service_type
for trove set

.. code-block:: bash

  export OS_DATABASE_SERVICE_TYPE=rax:database

Config Files
------------

`os-client-config` will look for a file called `clouds.yaml` in the following
locations:

* Current Directory
* ~/.config/openstack
* /etc/openstack

The first file found wins.

You can also set the environment variable `OS_CLIENT_CONFIG_FILE` to an
absolute path of a file to look for and that location will be inserted at the
front of the file search list.

The keys are all of the keys you'd expect from `OS_*` - except lower case
and without the OS prefix. So, region name is set with `region_name`.

Service specific settings, like the nova service type, are set with the
default service type as a prefix. For instance, to set a special service_type
for trove (because you're using Rackspace) set:

.. code-block:: yaml

  database_service_type: 'rax:database'


Site Specific File Locations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to `~/.config/openstack` and `/etc/openstack` - some platforms
have other locations they like to put things. `os-client-config` will also
look in an OS specific config dir

* `USER_CONFIG_DIR`
* `SITE_CONFIG_DIR`

`USER_CONFIG_DIR` is different on Linux, OSX and Windows.

* Linux: `~/.config/openstack`
* OSX: `~/Library/Application Support/openstack`
* Windows: `C:\\Users\\USERNAME\\AppData\\Local\\OpenStack\\openstack`

`SITE_CONFIG_DIR` is different on Linux, OSX and Windows.

* Linux: `/etc/openstack`
* OSX: `/Library/Application Support/openstack`
* Windows: `C:\\ProgramData\\OpenStack\\openstack`

An example config file is probably helpful:

.. code-block:: yaml

  clouds:
    mtvexx:
      profile: vexxhost
      auth:
        username: mordred@inaugust.com
        password: XXXXXXXXX
        project_name: mordred@inaugust.com
      region_name: ca-ymq-1
      dns_api_version: 1
    mordred:
      region_name: RegionOne
      auth:
        username: 'mordred'
        password: XXXXXXX
        project_name: 'shade'
        auth_url: 'https://montytaylor-sjc.openstack.blueboxgrid.com:5001/v2.0'
    infra:
      profile: rackspace
      auth:
        username: openstackci
        password: XXXXXXXX
        project_id: 610275
      regions:
      - DFW
      - ORD
      - IAD

You may note a few things. First, since `auth_url` settings are silly
and embarrassingly ugly, known cloud vendor profile information is included and
may be referenced by name. One of the benefits of that is that `auth_url`
isn't the only thing the vendor defaults contain. For instance, since
Rackspace lists `rax:database` as the service type for trove, `os-client-config`
knows that so that you don't have to. In case the cloud vendor profile is not
available, you can provide one called `clouds-public.yaml`, following the same
location rules previously mentioned for the config files.

`regions` can be a list of regions. When you call `get_all_clouds`,
you'll get a cloud config object for each cloud/region combo.

As seen with `dns_service_type`, any setting that makes sense to be per-service,
like `service_type` or `endpoint` or `api_version` can be set by prefixing
the setting with the default service type. That might strike you funny when
setting `service_type` and it does me too - but that's just the world we live
in.

Auth Settings
-------------

Keystone has auth plugins - which means it's not possible to know ahead of time
which auth settings are needed. `os-client-config` sets the default plugin type
to `password`, which is what things all were before plugins came about. In
order to facilitate validation of values, all of the parameters that exist
as a result of a chosen plugin need to go into the auth dict. For password
auth, this includes `auth_url`, `username` and `password` as well as anything
related to domains, projects and trusts.

Splitting Secrets
-----------------

In some scenarios, such as configuration management controlled environments,
it might be easier to have secrets in one file and non-secrets in another.
This is fully supported via an optional file `secure.yaml` which follows all
the same location rules as `clouds.yaml`. It can contain anything you put
in `clouds.yaml` and will take precedence over anything in the `clouds.yaml`
file.

.. code-block:: yaml

  # clouds.yaml
  clouds:
    internap:
      profile: internap
      auth:
        username: api-55f9a00fb2619
        project_name: inap-17037
      regions:
      - ams01
      - nyj01
  # secure.yaml
  clouds:
    internap:
      auth:
        password: XXXXXXXXXXXXXXXXX

SSL Settings
------------

When the access to a cloud is done via a secure connection, `os-client-config`
will always verify the SSL cert by default. This can be disabled by setting
`verify` to `False`. In case the cert is signed by an unknown CA, a specific
cacert can be provided via `cacert`. **WARNING:** `verify` will always have
precedence over `cacert`, so when setting a CA cert but disabling `verify`, the
cloud cert will never be validated.

Client certs are also configurable. `cert` will be the client cert file
location. In case the cert key is not included within the client cert file,
its file location needs to be set via `key`.

Cache Settings
--------------

Accessing a cloud is often expensive, so it's quite common to want to do some
client-side caching of those operations. To facilitate that, `os-client-config`
understands passing through cache settings to dogpile.cache, with the following
behaviors:

* Listing no config settings means you get a null cache.
* `cache.expiration_time` and nothing else gets you memory cache.
* Otherwise, `cache.class` and `cache.arguments` are passed in

Different cloud behaviors are also differently expensive to deal with. If you
want to get really crazy and tweak stuff, you can specify different expiration
times on a per-resource basis by passing values, in seconds to an expiration
mapping keyed on the singular name of the resource. A value of `-1` indicates
that the resource should never expire.

`os-client-config` does not actually cache anything itself, but it collects
and presents the cache information so that your various applications that
are connecting to OpenStack can share a cache should you desire.

.. code-block:: yaml

  cache:
    class: dogpile.cache.pylibmc
    expiration_time: 3600
    arguments:
      url:
        - 127.0.0.1
    expiration:
      server: 5
      flavor: -1
  clouds:
    mtvexx:
      profile: vexxhost
      auth:
        username: mordred@inaugust.com
        password: XXXXXXXXX
        project_name: mordred@inaugust.com
      region_name: ca-ymq-1
      dns_api_version: 1


IPv6
----

IPv6 is the future, and you should always use it if your cloud supports it and
if your local network supports it. Both of those are easily detectable and all
friendly software should do the right thing. However, sometimes you might
exist in a location where you have an IPv6 stack, but something evil has
caused it to not actually function. In that case, there is a config option
you can set to unbreak you `force_ipv4`, or `OS_FORCE_IPV4` boolean
environment variable.

.. code-block:: yaml

  client:
    force_ipv4: true
  clouds:
    mtvexx:
      profile: vexxhost
      auth:
        username: mordred@inaugust.com
        password: XXXXXXXXX
        project_name: mordred@inaugust.com
      region_name: ca-ymq-1
      dns_api_version: 1
    monty:
      profile: rax
      auth:
        username: mordred@inaugust.com
        password: XXXXXXXXX
        project_name: mordred@inaugust.com
      region_name: DFW

The above snippet will tell client programs to prefer returning an IPv4
address.

Per-region settings
-------------------

Sometimes you have a cloud provider that has config that is common to the
cloud, but also with some things you might want to express on a per-region
basis. For instance, Internap provides a public and private network specific
to the user in each region, and putting the values of those networks into
config can make consuming programs more efficient.

To support this, the region list can actually be a list of dicts, and any
setting that can be set at the cloud level can be overridden for that
region.

.. code-block:: yaml

  clouds:
    internap:
      profile: internap
      auth:
        password: XXXXXXXXXXXXXXXXX
        username: api-55f9a00fb2619
        project_name: inap-17037
      regions:
      - name: ams01
        values:
          networks:
          - name: inap-17037-WAN1654
            routes_externally: true
          - name: inap-17037-LAN6745
      - name: nyj01
        values:
          networks:
          - name: inap-17037-WAN1654
            routes_externally: true
          - name: inap-17037-LAN6745

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

Source
------

* Free software: Apache license
* Documentation: http://docs.openstack.org/developer/os-client-config
* Source: http://git.openstack.org/cgit/openstack/os-client-config
* Bugs: http://bugs.launchpad.net/os-client-config
