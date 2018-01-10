Meter API
=============

.. caution::
   BETA: This API is a work in progress and is subject to change.

For details on how to use meter, see :doc:`/user/guides/meter`

.. automodule:: openstack.meter.v2._proxy

The Meter Class
-------------------

The meter high-level interface is available through the ``meter``
member of a :class:`~openstack.connection.Connection` object.  The
``meter`` member will only be added if the service is detected.

Sample Operations
^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.meter.v2._proxy.Proxy

   .. automethod:: openstack.meter.v2._proxy.Proxy.find_sample
   .. automethod:: openstack.meter.v2._proxy.Proxy.samples

Statistic Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.meter.v2._proxy.Proxy

   .. automethod:: openstack.meter.v2._proxy.Proxy.find_statistics
   .. automethod:: openstack.meter.v2._proxy.Proxy.statistics

Resource Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.meter.v2._proxy.Proxy

   .. automethod:: openstack.meter.v2._proxy.Proxy.get_resource
   .. automethod:: openstack.meter.v2._proxy.Proxy.find_resource
   .. automethod:: openstack.meter.v2._proxy.Proxy.resources

Meter Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.meter.v2._proxy.Proxy

   .. automethod:: openstack.meter.v2._proxy.Proxy.find_meter
   .. automethod:: openstack.meter.v2._proxy.Proxy.meters

Capability Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.meter.v2._proxy.Proxy

   .. automethod:: openstack.meter.v2._proxy.Proxy.find_capability
   .. automethod:: openstack.meter.v2._proxy.Proxy.capabilities

The Alarm Class
---------------

The alarm high-level interface is available through the ``meter.alarm``
member of a :class:`~openstack.connection.Connection` object.  The
``meter.alarm`` member will only be added if the service is detected.

Alarm Operations
^^^^^^^^^^^^^^^^

.. autoclass:: openstack.meter.alarm.v2._proxy.Proxy

   .. automethod:: openstack.meter.alarm.v2._proxy.Proxy.create_alarm
   .. automethod:: openstack.meter.alarm.v2._proxy.Proxy.update_alarm
   .. automethod:: openstack.meter.alarm.v2._proxy.Proxy.delete_alarm
   .. automethod:: openstack.meter.alarm.v2._proxy.Proxy.get_alarm
   .. automethod:: openstack.meter.alarm.v2._proxy.Proxy.find_alarm
   .. automethod:: openstack.meter.alarm.v2._proxy.Proxy.alarms


Alarm Change Operations
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.meter.alarm.v2._proxy.Proxy

   .. automethod:: openstack.meter.alarm.v2._proxy.Proxy.find_alarm_change
   .. automethod:: openstack.meter.alarm.v2._proxy.Proxy.alarm_changes
