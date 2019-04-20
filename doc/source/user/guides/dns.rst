Using OpenStack DNS
===================

Before working with the DNS service, you'll need to create a connection
to your OpenStack cloud by following the :doc:`connect` user guide. This will
provide you with the ``conn`` variable used in the examples below.

.. TODO(gtema): Implement this guide

List Zones
----------

.. literalinclude:: ../examples/dns/list.py
   :pyobject: list_zones

Full example: `dns resource list`_

.. _dns resource list: https://opendev.org/openstack/openstacksdk/src/branch/master/examples/dns/list.py
