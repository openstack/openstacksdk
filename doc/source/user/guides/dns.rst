Using OpenStack DNS
===================

Before working with the DNS service, you'll need to create a connection
to your OpenStack cloud by following the :doc:`connect` user guide. This will
provide you with the ``conn`` variable used in the examples below.

.. contents:: Table of Contents
   :local:

The primary resource of the DNS service is the server.

List Zones
----------

**Zone** is a logical grouping of DNS records for a domain, allowing for the
centralized management of DNS resources, including domain names,
nameservers, and DNS queries.

.. literalinclude:: ../examples/dns/list.py
   :pyobject: list_zones

Full example: `dns resource list`_

List Recordsets
---------------

**Recordsets** allow for the centralized management of various DNS records
within a Zone, helping to define how a domain responds to different types
of DNS queries.

.. literalinclude:: ../examples/dns/list.py
   :pyobject: list_recordsets

Full example: `dns resource list`_

Create Zone
-----------

Create a zone.
It allows users to define and manage the DNS namespace for a particular domain.

.. literalinclude:: ../examples/dns/create.py
   :pyobject: create_zone

Full example: `dns resource list`_

Create Recordset
----------------

Create a recordset. It accepts several parameters that define the DNS
record's properties and sends an API request to OpenStack to create the
recordset within a specified DNS zone.

.. literalinclude:: ../examples/dns/create.py
   :pyobject: create_recordset

Full example: `dns resource list`_

Delete Zone
-----------

Delete a zone.
It allows users to completely delete the DNS management for a specified domain.

.. literalinclude:: ../examples/dns/delete.py
   :pyobject: delete_zone

Full example: `dns resource list`_

Delete Recordset
----------------

Delete a recordset.

.. literalinclude:: ../examples/dns/delete.py
   :pyobject: delete_recordset

Full example: `dns resource list`_

Find Zone
---------

The find_zone function searches for and returns a DNS zone by its name
using a given connection object.

.. literalinclude:: ../examples/dns/find.py
   :pyobject: find_zone

Full example: `dns resource list`_

Find Recordset
--------------

The find_recordset function searches for a DNS recordset
with a specific name and type
within a given zone. If multiple recordsets
with the same name exist,
the record type can be specified to find the exact match.

.. literalinclude:: ../examples/dns/find.py
   :pyobject: find_recordset

Full example: `dns resource list`_

.. _dns resource list: https://opendev.org/openstack/openstacksdk/src/branch/master/examples/dns/list.py
.. _dns resource create: https://opendev.org/openstack/openstacksdk/src/branch/master/examples/dns/create.py
.. _dns resource delete: https://opendev.org/openstack/openstacksdk/src/branch/master/examples/dns/delete.py
.. _dns resource find: https://opendev.org/openstack/openstacksdk/src/branch/master/examples/dns/find.py
