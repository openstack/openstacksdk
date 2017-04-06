Telemetry API
=============

.. caution::
   BETA: This API is a work in progress and is subject to change.

For details on how to use telemetry, see :doc:`/users/guides/telemetry`

.. automodule:: openstack.telemetry.v2._proxy

The Telemetry Class
-------------------

The telemetry high-level interface is available through the ``telemetry``
member of a :class:`~openstack.connection.Connection` object.  The
``telemetry`` member will only be added if the service is detected.

Sample Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.telemetry.v2._proxy.Proxy

   .. automethod:: openstack.telemetry.v2._proxy.Proxy.find_sample
   .. automethod:: openstack.telemetry.v2._proxy.Proxy.samples

Statistic Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.telemetry.v2._proxy.Proxy

   .. automethod:: openstack.telemetry.v2._proxy.Proxy.find_statistics
   .. automethod:: openstack.telemetry.v2._proxy.Proxy.statistics

Resource Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.telemetry.v2._proxy.Proxy

   .. automethod:: openstack.telemetry.v2._proxy.Proxy.get_resource
   .. automethod:: openstack.telemetry.v2._proxy.Proxy.find_resource
   .. automethod:: openstack.telemetry.v2._proxy.Proxy.resources

Meter Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.telemetry.v2._proxy.Proxy

   .. automethod:: openstack.telemetry.v2._proxy.Proxy.find_meter
   .. automethod:: openstack.telemetry.v2._proxy.Proxy.meters

Capability Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.telemetry.v2._proxy.Proxy

   .. automethod:: openstack.telemetry.v2._proxy.Proxy.find_capability
   .. automethod:: openstack.telemetry.v2._proxy.Proxy.capabilities

The Alarm Class
---------------

The alarm high-level interface is available through the ``telemetry.alarm``
member of a :class:`~openstack.connection.Connection` object.  The
``telemetry.alarm`` member will only be added if the service is detected.

Alarm Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.telemetry.alarm.v2._proxy.Proxy

   .. automethod:: openstack.telemetry.alarm.v2._proxy.Proxy.create_alarm
   .. automethod:: openstack.telemetry.alarm.v2._proxy.Proxy.update_alarm
   .. automethod:: openstack.telemetry.alarm.v2._proxy.Proxy.delete_alarm
   .. automethod:: openstack.telemetry.alarm.v2._proxy.Proxy.get_alarm
   .. automethod:: openstack.telemetry.alarm.v2._proxy.Proxy.find_alarm
   .. automethod:: openstack.telemetry.alarm.v2._proxy.Proxy.alarms


Alarm Change Operations
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.telemetry.alarm.v2._proxy.Proxy

   .. automethod:: openstack.telemetry.alarm.v2._proxy.Proxy.find_alarm_change
   .. automethod:: openstack.telemetry.alarm.v2._proxy.Proxy.alarm_changes
