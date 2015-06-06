===============================
os-client-config
===============================

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
for trove set::

  export OS_DATABASE_SERVICE_TYPE=rax:database

Config Files
------------

`os-client-config` will look for a file called `clouds.yaml` in the following
locations:

* Current Directory
* ~/.config/openstack
* /etc/openstack

The first file found wins.

The keys are all of the keys you'd expect from `OS_*` - except lower case
and without the OS prefix. So, region name is set with `region_name`.

Service specific settings, like the nova service type, are set with the
default service type as a prefix. For instance, to set a special service_type
for trove (because you're using Rackspace) set:

::

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

::

  clouds:
    mordred:
      profile: hp
      auth:
        username: mordred@inaugust.com
        password: XXXXXXXXX
        project_name: mordred@inaugust.com
      region_name: region-b.geo-1
      dns_service_type: hpext:dns
      compute_api_version: 1.1
    monty:
      auth:
        auth_url: https://region-b.geo-1.identity.hpcloudsvc.com:35357/v2.0
        username: monty.taylor@hp.com
        password: XXXXXXXX
        project_name: monty.taylor@hp.com-default-tenant
      region_name: region-b.geo-1
      dns_service_type: hpext:dns
    infra:
      profile: rackspace
      auth:
        username: openstackci
        password: XXXXXXXX
        project_id: 610275
      region_name: DFW,ORD,IAD

You may note a few things. First, since `auth_url` settings are silly
and embarrasingly ugly, known cloud vendor profile information is included and
may be referenced by name. One of the benefits of that is that `auth_url`
isn't the only thing the vendor defaults contain. For instance, since
Rackspace lists `rax:database` as the service type for trove, `os-client-config`
knows that so that you don't have to. In case the cloud vendor profile is not
available, you can provide one called `clouds-public.yaml`, following the same
location rules previously mentioned for the config files.

Also, `region_name` can be a list of regions. When you call `get_all_clouds`,
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
* `cache.max_age` and nothing else gets you memory cache.
* Otherwise, `cache.class` and `cache.arguments` are passed in

`os-client-config` does not actually cache anything itself, but it collects
and presents the cache information so that your various applications that
are connecting to OpenStack can share a cache should you desire.

::

  cache:
    class: dogpile.cache.pylibmc
    max_age: 3600
    arguments:
      url:
        - 127.0.0.1
  clouds:
    mordred:
      profile: hp
      auth:
        username: mordred@inaugust.com
        password: XXXXXXXXX
        project_name: mordred@inaugust.com
      region_name: region-b.geo-1
      dns_service_type: hpext:dns


Usage
-----

The simplest and least useful thing you can do is:
::

  python -m os_client_config.config

Which will print out whatever if finds for your config. If you want to use
it from python, which is much more likely what you want to do, things like:

Get a named cloud.
::

  import os_client_config

  cloud_config = os_client_config.OpenStackConfig().get_one_cloud(
      'hp', 'region-b.geo-1')
  print(cloud_config.name, cloud_config.region, cloud_config.config)

Or, get all of the clouds.
::
  import os_client_config

  cloud_config = os_client_config.OpenStackConfig().get_all_clouds()
  for cloud in cloud_config:
      print(cloud.name, cloud.region, cloud.config)
