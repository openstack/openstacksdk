====================
Statistics reporting
====================

`openstacksdk` offers possibility to report statistics on individual API
requests/responses in different formats. `Statsd` allows reporting of the
response times in the statsd format. `InfluxDB` allows a more event-oriented
reporting of the same data. `Prometheus` reporting is a bit different and
requires the application using SDK to take care of the metrics exporting, while
`openstacksdk` prepares the metrics.

Due to the nature of the `statsd` protocol lots of tools consuming the metrics
do the data aggregation and processing in the configurable time frame (mean
value calculation for a 1 minute time frame). For the case of periodic tasks
this might not be very useful. A better fit for using `openstacksdk` as a
library is an 'event'-recording, where duration of an individual request is
stored and all required calculations are done if necessary in the monitoring
system based required timeframe, or the data is simply shown as is with no
analytics. A `comparison
<https://prometheus.io/docs/introduction/comparison/>`_ article describes
differences in those approaches.

Simple Usage
------------

To receive metrics add a following section to the config file (clouds.yaml):

.. code-block:: yaml

   metrics:
     statsd:
       host: __statsd_server_host__
       port: __statsd_server_port__
   clouds:
     ..


In order to enable InfluxDB reporting following configuration need to be done
in the `clouds.yaml` file

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

Metrics will be reported only when corresponding client libraries (
`statsd` for 'statsd' reporting, `influxdb` for influxdb reporting
correspondingly). When those libraries are not available reporting will be
silently ignored.

InfluxDB reporting allows setting additional tags into the metrics based on the
selected cloud.

.. code-block:: yaml

  clouds:
    my_cloud:
      profile: some_profile
      ...
      additional_metric_tags:
        environment: production
