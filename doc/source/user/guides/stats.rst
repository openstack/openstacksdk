====================
Statistics reporting
====================

`openstacksdk` can report statistics on individual API
requests/responses in several different formats.

Note that metrics will be reported only when corresponding client
libraries (`statsd` for 'statsd' reporting, `influxdb` for influxdb,
etc.).  If libraries are not available reporting will be silently
ignored.

statsd
------

`statsd` can be configured via configuration entries or environment
variables.

A global `metrics` entry defines defaults for all clouds.  Each cloud
can specify a `metrics` section to override variables; this may be
useful to separate results reported for each cloud.

.. code-block:: yaml

   metrics:
     statsd:
       host: __statsd_server_host__
       port: __statsd_server_port__
       prefix: __statsd_prefix__ (default 'openstack.api')
   clouds:
     a-cloud:
       auth:
        ...
       metrics:
         statsd:
           prefix: 'openstack.api.a-cloud'

If the `STATSD_HOST` or `STATSD_PORT` environment variables are set,
they will be taken as the default values (and enable `statsd`
reporting if no other configuration is specified).

InfluxDB
--------

`InfluxDB <https://www.influxdata.com/>`__ is supported via
configuration in the `metrics` field.  Similar to `statsd`, each cloud
can provide it's own `metrics` section to override any global
defaults.

.. code-block:: yaml

   metrics:
     influxdb:
       host: __influxdb_server_host__
       port: __influxdb_server_port__
       use_udp: __True|False__
       username: __influxdb_auth_username__
       password: __influxdb_auth_password__
       database: __influxdb_db_name__
       measurement: __influxdb_measurement_name__
       timeout: __infludb_requests_timeout__
   clouds:
     ..

InfluxDB reporting allows setting additional tags into the metrics based on the
selected cloud.

.. code-block:: yaml

  clouds:
    my_cloud:
      profile: some_profile
      ...
      additional_metric_tags:
        environment: production

prometheus
----------
..
   NOTE(ianw) 2021-04-19 : examples here would be great; this is just terse
   description taken from
   https://review.opendev.org/c/openstack/openstacksdk/+/614834

The prometheus support does not read from config, and does not run an
http service since OpenstackSDK is a library. It is expected that an
application that uses OpenstackSDK and wants request stats be
collected will pass a `prometheus_client.CollectorRegistry` to
`collector_registry`.
