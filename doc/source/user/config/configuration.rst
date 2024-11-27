.. _openstack-config:

======================================
Configuring OpenStack SDK Applications
======================================

.. _config-environment-variables:

Environment Variables
---------------------

`openstacksdk` honors all of the normal `OS_*` variables. It does not
provide backwards compatibility to service-specific variables such as
`NOVA_USERNAME`.

If you have OpenStack environment variables set, `openstacksdk` will
produce a cloud config object named `envvars` containing your values from the
environment. If you don't like the name `envvars`, that's ok, you can override
it by setting `OS_CLOUD_NAME`.

Service specific settings, like the nova service type, are set with the
default service type as a prefix. For instance, to set a special service_type
for trove set

.. code-block:: bash

  export OS_DATABASE_SERVICE_TYPE=rax:database

.. _config-clouds-yaml:

Config Files
------------

`openstacksdk` will look for a file called `clouds.yaml` in the following
locations:

* ``.`` (the current directory)
* ``$HOME/.config/openstack``
* ``/etc/openstack``

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
have other locations they like to put things. `openstacksdk` will also
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
      profile: https://vexxhost.com
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
may be referenced by name or by base URL to the cloud in question if the
cloud serves a vendor profile. One of the benefits of that is that `auth_url`
isn't the only thing the vendor defaults contain. For instance, since
Rackspace lists `rax:database` as the service type for trove, `openstacksdk`
knows that so that you don't have to. In case the cloud vendor profile is not
available, you can provide one called `clouds-public.yaml`, following the same
location rules previously mentioned for the config files.

`regions` can be a list of regions. When you call `get_all_clouds`,
you'll get a cloud config object for each cloud/region combo.

As seen with `dns_service_type`, any setting that makes sense to be
per-service, like `service_type` or `endpoint` or `api_version` can be set
by prefixing the setting with the default service type. That might strike you
funny when setting `service_type` and it does me too - but that's just the
world we live in.

Auth Settings
-------------

Keystone has auth plugins - which means it's not possible to know ahead of time
which auth settings are needed. `openstacksdk` sets the default plugin type
to `password`, which is what things all were before plugins came about. In
order to facilitate validation of values, all of the parameters that exist
as a result of a chosen plugin need to go into the auth dict. For password
auth, this includes `auth_url`, `username` and `password` as well as anything
related to domains, projects and trusts.

API Settings
------------

The following settings are passed to keystoneauth and are common to
all services.

``api_timeout``
    A timeout for API requests. This should be a numerical value
    indicating some amount (or fraction) of seconds or 0 for no
    timeout. (optional, defaults to 0)

``collect_timing``
    Whether or not to collect per-method timing information for each
    API call. (optional, defaults to False)

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

When the access to a cloud is done via a secure connection, `openstacksdk`
will always verify the SSL cert by default. This can be disabled by setting
`verify` to `False`. In case the cert is signed by an unknown CA, a specific
cacert can be provided via `cacert`. **WARNING:** `verify` will always have
precedence over `cacert`, so when setting a CA cert but disabling `verify`, the
cloud cert will never be validated.

Client certs are also configurable. `cert` will be the client cert file
location. In case the cert key is not included within the client cert file,
its file location needs to be set via `key`.

.. code-block:: yaml

  # clouds.yaml
  clouds:
    regular-secure-cloud:
      auth:
        auth_url: https://signed.cert.domain:5000
        ...
    unknown-ca-with-client-cert-secure-cloud:
      auth:
        auth_url: https://unknown.ca.but.secure.domain:5000
        ...
      key: /home/myhome/client-cert.key
      cert: /home/myhome/client-cert.crt
      cacert: /home/myhome/ca.crt
    self-signed-insecure-cloud:
      auth:
        auth_url: https://self.signed.cert.domain:5000
        ...
      verify: False

Note for parity with ``openstack`` command-line options the `insecure`
boolean is also recognised (with the opposite semantics to `verify`;
i.e. `True` ignores certificate failures).  This should be considered
deprecated for `verify`.


Cache Settings
--------------

.. versionchanged:: 1.0.0

   Previously, caching was managed exclusively in the cloud layer. Starting in
   openstacksdk 1.0.0, caching is moved to the proxy layer. As the cloud layer
   depends on the proxy layer in 1.0.0, this means both layers can benefit from
   the cache.

Authenticating and accessing resources on a cloud is often expensive. It is
therefore quite common that applications will wish to do some client-side
caching of both credentials and cloud resources. To facilitate this,
*openstacksdk* supports caching credentials and resources using the system
keyring and *dogpile.cache*, respectively.

.. tip::

   It is important to emphasise that *openstacksdk* does not actually cache
   anything itself. Rather, it collects and presents the cache information
   so that your various applications that are connecting to OpenStack can share
   a cache should you desire. It is important that your cache backend is
   correctly configured according to the needs of your application.

Caching in enabled or disabled globally, rather than on a cloud-by-cloud basis.
This is done by setting configuring the``cache`` top-level key. Caching of
authentication tokens can be configured using the following settings:

``cache.auth``
  A boolean indicating whether tokens should be cached in the keyring.
  When enabled, this allows the consequent connections to the same cloud to
  skip fetching new token. When the token expires or is invalidated,
  `openstacksdk` will automatically establish a new connection.
  Defaults to ``false``.

For example, to configure caching of authentication tokens.

.. code-block:: yaml

  cache:
    auth: true

Caching of resources can be configured using the following settings:

``cache.expiration_time``
    The expiration time in seconds for a cache entry.
    This should be an integer.
    Defaults to ``0``.

``cache.class``
  The cache backend to use, which can include any backend supported by
  *dogpile.cache* natively as well as backend provided by third-part packages.
  This should be a string.
  Defaults to ``dogpile.cache.memory``.

``cache.arguments``
  A mapping of arbitrary arguments to pass into the cache backend. These are
  backend specific. Keys should correspond to a configuration option for the
  configured cache backend.
  Defaults to ``{}``.

``cache.expirations``
  A mapping of resource types to expiration times. The keys should be specified
  in the same way as the metrics are emitted, by joining meaningful resource
  URL segments with ``.``. For example, both ``/servers`` and ``/servers/ID``
  should be specified as ``servers``, while ``/servers/ID/metadata/KEY`` should
  be specified as `server.metadata`. Values should be an expiration time in
  seconds. A value of ``-1`` indicates that the cache should never expire,
  while a value of ``0`` disables caching for the resource.
  Defaults to ``{}``

For example, to configure caching with the ``dogpile.cache.memory`` backend
with a 1 hour expiration.

.. code-block:: yaml

   cache:
     expiration_time: 3600

To configure caching with the ``dogpile.cache.memory`` backend with a 1 hour
expiration but only for requests to the OpenStack Compute service's
``/servers`` API:

.. code-block:: yaml

   cache:
     expirations:
       servers: 3600

To configure caching with the ``dogpile.cache.pylibmc`` backend with a 1 hour
expiration time and a memcached server running on your localhost.

.. code-block:: yaml

   cache:
     expiration_time: 3600
     arguments:
       url:
       - 127.0.0.1

To configure caching with the ``dogpile.cache.pylibmc`` backend with a 1 hour
expiration time, a memcached server running on your localhost, and multiple
per-resource cache expiration times.

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
      compute.servers: 5
      compute.flavors: -1
      image.images: 5

Finally, if the ``cache`` key is undefined, a null cache is enabled meaning
caching is effectively disabled.

.. note::

   Non ``GET`` requests cause cache invalidation based on the caching key
   prefix. This means that, for example, a ``PUT`` request to ``/images/ID``
   will invalidate all images cache (list and all individual entries). Moreover
   it is possible to explicitly pass the ``skip_cache`` parameter to the
   ``proxy._get`` function to bypass cache and invalidate what is already
   there. This is happening automatically in the ``wait_for_status`` methods
   where it is expected that resource will change some of the attributes over
   the time. Forcing complete cache invalidation can be achieved calling
   ``conn._cache.invalidate``

MFA Support
-----------

MFA support requires a specially prepared configuration file. In this case a
combination of two different authorization plugins is used with their
individual requirements to the specified parameters.

.. code-block:: yaml

  clouds:
    mfa:
      auth_type: "v3multifactor"
      auth_methods:
        - v3password
        - v3totp
      auth:
        auth_url: https://identity.cloud.com
        username: user
        user_id: uid
        password: XXXXXXXXX
        project_name: project
        user_domain_name: udn
        project_domain_name: pdn


IPv6
----

IPv6 is the future, and you should always use it if your cloud
supports it and if your local network supports it. Both of those are
easily detectable and all friendly software should do the right thing.

However, sometimes a cloud API may return IPv6 information that is not
useful to a production deployment.  For example, the API may provide
an IPv6 address for a server, but not provide that to the host
instance via metadata (configdrive) or standard IPv6 autoconfiguration
methods (i.e. the host either needs to make a bespoke API call, or
otherwise statically configure itself).

For such situations, you can set the ``force_ipv4``, or ``OS_FORCE_IPV4``
boolean environment variable.  For example:

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
    monty:
      profile: fooprovider
      force_ipv4: true
      auth:
        username: mordred@inaugust.com
        password: XXXXXXXXX
        project_name: mordred@inaugust.com
      region_name: RegionFoo

The above snippet will tell client programs to prefer the IPv4 address
and leave the ``public_v6`` field of the `Server` object blank for the
``fooprovider`` cloud .  You can also set this with a client flag for
all clouds:

.. code-block:: yaml

  client:
    force_ipv4: true


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


Setting Precedence
------------------

Some settings are redundant, e.g. ``project-name`` and ``project-id`` both
specify the project. In a conflict between redundant settings, the
``_name`` ``clouds.yaml`` option (or equivalent ``-name`` CLI option and ``_NAME`` environment variable) will be used.

Some environment variables or commandline flags can override the settings from
clouds.yaml. These are:

- ``--domain-id`` (``OS_DOMAIN_ID``)
- ``--domain-name`` (``OS_DOMAIN_NAME``)
- ``--user-domain-id`` (``OS_USER_DOMAIN_ID``)
- ``--user-domain-name`` (``OS_USER_DOMAIN_NAME``)
- ``--project-domain-id`` (``OS_PROJECT_DOMAIN_ID``)
- ``--project-domain-name`` (``OS_PROJECT_DOMAIN_NAME``)
- ``--auth-token`` (``OS_AUTH_TOKEN``)
- ``--project-id`` (``OS_PROJECT_ID``)
- ``--project-name`` (``OS_PROJECT_NAME``)
- ``--tenant-id`` (``OS_TENANT_ID``) (deprecated for ``--project-id``)
- ``--tenant-name`` (``OS_TENANT_NAME``) (deprecated for ``--project-name``)

Similarly, if one of the above settings is specified in ``clouds.yaml`` as
part of the ``auth`` section as well as the main section, the ``auth`` settings
will be overridden. For example in this config section, note that project is
specified multiple times:

.. code-block:: yaml

  clouds:
    mtvexx:
      profile: https://vexxhost.com
      auth:
        username: mordred@inaugust.com
        password: XXXXXXXXX
        project_name: mylessfavoriteproject
        project_id: 0bedab75-898c-4521-a038-0b4b71c41bed
      region_name: ca-ymq-1
      project_name: myfavoriteproject
      project_id: 2acf9403-25e8-479e-a3c6-d67540c424a4

In the above example, the ``project_id`` configuration values will be ignored
in favor of the ``project_name`` configuration values, and the higher-level
project will be chosen over the auth-specified project. So the actual project
used will be ```myfavoriteproject```.


Examples
--------

``auth``
~~~~~~~~

.. rubric:: Password-based authentication (project-scoped)

.. code-block:: yaml

    example:
        auth:
            auth_url: http://example.com/identity
            password: password
            project_domain_id: default
            project_name: admin
            user_domain_id: default
            username: admin
        region_name: RegionOne

.. rubric:: Password-based authentication (domain-scoped)

.. code-block:: yaml

    example:
        auth:
            auth_url: http://example.com/identity
            domain_id: default
            password: password
            username: admin
        region_name: RegionOne

.. rubric:: Password-based authentication (trust-scoped)

.. code-block:: yaml

    example-trust:
        auth:
            auth_url: http://example.com/identity
            password: password
            username: admin
            trust_id: 95946f9eef864fdc993079d8fe3e5747
        region_name: RegionOne

.. rubric:: Password-based authentication (system-scoped)

.. code-block:: yaml

    example-system:
        auth:
            auth_url: http://example.com/identity
            password: password
            system_scope: all
            username: admin
        region_name: RegionOne

.. rubric:: Application credential-based authentication

.. code-block:: yaml

    example-appcred:
        auth:
            auth_url: http://example.com/identity
            application_credential_id: 9da0a8da3d394d09bf49dfc27014d254
            application_credential_secret: pKfDSvUOFwO2t2_XxCajAFhzCKAVHI7yfqPb6xjshVDnMUHF7ifju8gMdhHTI4Eo56UP_hEc8ssmgA1NNtKMpA
        auth_type: v3applicationcredential
        region_name: RegionOne

.. rubric:: Token-based authentication

.. code-block:: yaml

    example-token:
        auth:
            auth_url: http://example.com/identity
            token: gAAAAABl32ptw2PN6L9JyBeO16PwQU1SrdMUvUz8Eon7LC2PFItdGRWFpOkK0qwH3JkukTuEM5qbYK9ucowRXET1RBMjZlfVpUa8Nz3qjQdzXw7pBKH4w1e4tekvDCOKfn15ZoujBOvdGqgtpW-febVGaW9oJzf6R3WTMDxWz3YRJjmiOBpwcN8
            project_id: 1fd93a4455c74d2ea94b929fc5f0e488
        auth_type: v3token
        region_name: RegionOne

.. note::

    This is a toy example: by their very definition tokens are short-lived.
    You are unlikely to store them in a ``clouds.yaml`` file.
    Instead, you would likely pass the TOTP token via the command line
    (``--os-token``) or as an environment variable (``OS_TOKEN``).

.. rubric:: TOTP-based authentication

.. code-block:: yaml

    example-totp:
        auth:
            auth_url: http://example.com/identity
            passcode: password
            project_domain_id: default
            project_name: admin
            user_domain_id: default
            username: admin
        auth_type: v3totp
        region_name: RegionOne

.. note::

    This is a toy example: by their very definition TOTP tokens are
    short-lived. You are unlikely to store them in a ``clouds.yaml`` file.
    Instead, you would likely pass the TOTP token via the command line
    (``--os-passcode``) or as an environment variable (``OS_PASSCODE``).

.. rubric:: OAuth1-based authentication

.. code-block:: yaml

    example-oauth:
        auth:
            auth_url: http://example.com/identity
            consumer_key: foo
            consumer_secret: secret
            access_key: bar
            access_secret: secret
        auth_type: v3oauth1
        region_name: RegionOne
