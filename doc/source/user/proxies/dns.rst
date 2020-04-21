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
  :noindex:
  :members: create_zone, delete_zone, get_zone, find_zone, zones,
            abandon_zone, xfr_zone

Recordset Operations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.dns.v2._proxy.Proxy
  :noindex:
  :members: create_recordset, update_recordset, get_recordset,
            delete_recordset, recordsets

Zone Import Operations
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.dns.v2._proxy.Proxy
  :noindex:
  :members: zone_imports, create_zone_import, get_zone_import,
            delete_zone_import

Zone Export Operations
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.dns.v2._proxy.Proxy
  :noindex:
  :members: zone_exports, create_zone_export, get_zone_export,
            get_zone_export_text, delete_zone_export

FloatingIP Operations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.dns.v2._proxy.Proxy
  :noindex:
  :members: floating_ips, get_floating_ip, update_floating_ip

Zone Transfer Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: openstack.dns.v2._proxy.Proxy
  :noindex:
  :members: zone_transfer_requests, get_zone_transfer_request,
            create_zone_transfer_request, update_zone_transfer_request,
            delete_zone_transfer_request, zone_transfer_accepts,
            get_zone_transfer_accept, create_zone_transfer_accept
