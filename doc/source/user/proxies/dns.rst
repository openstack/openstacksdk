DNS API
=======

For details on how to use dns, see :doc:`/user/guides/dns`

.. automodule:: openstack.dns.v2._proxy

The DNS Class
-------------

The dns high-level interface is available through the ``dns``
member of a :class:`~openstack.connection.Connection` object.  The
``dns`` member will only be added if the service is detected.

DNS Zone Operations
^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.dns.v2._proxy.Proxy

   .. automethod:: openstack.dns.v2._proxy.Proxy.create_zone
   .. automethod:: openstack.dns.v2._proxy.Proxy.delete_zone
   .. automethod:: openstack.dns.v2._proxy.Proxy.get_zone
   .. automethod:: openstack.dns.v2._proxy.Proxy.find_zone
   .. automethod:: openstack.dns.v2._proxy.Proxy.zones
   .. automethod:: openstack.dns.v2._proxy.Proxy.abandon_zone
   .. automethod:: openstack.dns.v2._proxy.Proxy.xfr_zone

Recordset Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.dns.v2._proxy.Proxy

   .. automethod:: openstack.dns.v2._proxy.Proxy.create_recordset
   .. automethod:: openstack.dns.v2._proxy.Proxy.update_recordset
   .. automethod:: openstack.dns.v2._proxy.Proxy.get_recordset
   .. automethod:: openstack.dns.v2._proxy.Proxy.delete_recordset
   .. automethod:: openstack.dns.v2._proxy.Proxy.recordsets

Zone Import Operations
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.dns.v2._proxy.Proxy

   .. automethod:: openstack.dns.v2._proxy.Proxy.zone_imports
   .. automethod:: openstack.dns.v2._proxy.Proxy.create_zone_import
   .. automethod:: openstack.dns.v2._proxy.Proxy.get_zone_import
   .. automethod:: openstack.dns.v2._proxy.Proxy.delete_zone_import

Zone Export Operations
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.dns.v2._proxy.Proxy

   .. automethod:: openstack.dns.v2._proxy.Proxy.zone_exports
   .. automethod:: openstack.dns.v2._proxy.Proxy.create_zone_export
   .. automethod:: openstack.dns.v2._proxy.Proxy.get_zone_export
   .. automethod:: openstack.dns.v2._proxy.Proxy.get_zone_export_text
   .. automethod:: openstack.dns.v2._proxy.Proxy.delete_zone_export

FloatingIP Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.dns.v2._proxy.Proxy

   .. automethod:: openstack.dns.v2._proxy.Proxy.floating_ips
   .. automethod:: openstack.dns.v2._proxy.Proxy.get_floating_ip
   .. automethod:: openstack.dns.v2._proxy.Proxy.update_floating_ip

Zone Transfer Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.dns.v2._proxy.Proxy

   .. automethod:: openstack.dns.v2._proxy.Proxy.zone_transfer_requests
   .. automethod:: openstack.dns.v2._proxy.Proxy.get_zone_transfer_request
   .. automethod:: openstack.dns.v2._proxy.Proxy.create_zone_transfer_request
   .. automethod:: openstack.dns.v2._proxy.Proxy.update_zone_transfer_request
   .. automethod:: openstack.dns.v2._proxy.Proxy.delete_zone_transfer_request
   .. automethod:: openstack.dns.v2._proxy.Proxy.zone_transfer_accepts
   .. automethod:: openstack.dns.v2._proxy.Proxy.get_zone_transfer_accept
   .. automethod:: openstack.dns.v2._proxy.Proxy.create_zone_transfer_accept
