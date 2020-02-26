Getting started with the OpenStack SDK
======================================

For a listing of terms used throughout the SDK, including the names of
projects and services supported by it, see the :doc:`glossary <../glossary>`.

Installation
------------

The OpenStack SDK is available on
`PyPI <https://pypi.org/project/openstacksdk>`_ under the name
**openstacksdk**. To install it, use ``pip``::

   $ pip install openstacksdk

To check the installed version you can call the module with ::

   $ python -m openstack version

.. _user_guides:

User Guides
-----------

These guides walk you through how to make use of the libraries we provide
to work with each OpenStack service. If you're looking for a cookbook
approach, this is where you'll want to begin.

.. toctree::
   :maxdepth: 1

   Configuration <config/index>
   Connect to an OpenStack Cloud <guides/connect>
   Connect to an OpenStack Cloud Using a Config File <guides/connect_from_config>
   Logging <guides/logging>
   Statistics reporting <guides/stats>
   Microversions <microversions>
   Baremetal <guides/baremetal>
   Block Storage <guides/block_storage>
   Clustering <guides/clustering>
   Compute <guides/compute>
   Database <guides/database>
   DNS <guides/dns>
   Identity <guides/identity>
   Image <guides/image>
   Key Manager <guides/key_manager>
   Message <guides/message>
   Network <guides/network>
   Object Store <guides/object_store>
   Orchestration <guides/orchestration>

API Documentation
-----------------

Service APIs are exposed through a two-layered approach. The classes
exposed through our *Connection* interface are the place to start if you're
an application developer consuming an OpenStack cloud. The *Resource*
interface is the layer upon which the *Connection* is built, with
*Connection* methods accepting and returning *Resource* objects.

The Cloud Abstraction layer has a data model.

.. toctree::
   :maxdepth: 1

   model

Connection Interface
~~~~~~~~~~~~~~~~~~~~

A *Connection* instance maintains your cloud config, session and authentication
information providing you with a set of higher-level interfaces to work with
OpenStack services.

.. toctree::
   :maxdepth: 1

   connection

Once you have a *Connection* instance, services are accessed through instances
of :class:`~openstack.proxy.Proxy` or subclasses of it that exist as
attributes on the :class:`~openstack.connection.Connection`.

.. _service-proxies:

Service Proxies
~~~~~~~~~~~~~~~

The following service proxies exist on the
:class:`~openstack.connection.Connection`. The service proxies are all always
present on the :class:`~openstack.connection.Connection` object, but the
combination of your ``CloudRegion`` and the catalog of the cloud in question
control which services can be used.

.. toctree::
   :maxdepth: 1

   Accelerator <proxies/accelerator>
   Baremetal <proxies/baremetal>
   Baremetal Introspection <proxies/baremetal_introspection>
   Block Storage <proxies/block_storage>
   Clustering <proxies/clustering>
   Compute <proxies/compute>
   Database <proxies/database>
   DNS <proxies/dns>
   Identity v2 <proxies/identity_v2>
   Identity v3 <proxies/identity_v3>
   Image v1 <proxies/image_v1>
   Image v2 <proxies/image_v2>
   Key Manager <proxies/key_manager>
   Load Balancer <proxies/load_balancer_v2>
   Message v2 <proxies/message_v2>
   Network <proxies/network>
   Object Store <proxies/object_store>
   Orchestration <proxies/orchestration>
   Workflow <proxies/workflow>

Resource Interface
~~~~~~~~~~~~~~~~~~

The *Resource* layer is a lower-level interface to communicate with OpenStack
services. While the classes exposed by the *Connection* build a convenience
layer on top of this, *Resources* can be used directly. However, the most
common usage of this layer is in receiving an object from a class in the
*Connection* layer, modifying it, and sending it back into the *Connection*
layer, such as to update a resource on the server.

The following services have exposed *Resource* classes.

.. toctree::
   :maxdepth: 1

   Accelerator <resources/accelerator/index>
   Baremetal <resources/baremetal/index>
   Baremetal Introspection <resources/baremetal_introspection/index>
   Block Storage <resources/block_storage/index>
   Clustering <resources/clustering/index>
   Compute <resources/compute/index>
   Database <resources/database/index>
   DNS <resources/dns/index>
   Identity <resources/identity/index>
   Image <resources/image/index>
   Key Management <resources/key_manager/index>
   Load Balancer <resources/load_balancer/index>
   Network <resources/network/index>
   Orchestration <resources/orchestration/index>
   Object Store <resources/object_store/index>
   Workflow <resources/workflow/index>

Low-Level Classes
~~~~~~~~~~~~~~~~~

The following classes are not commonly used by application developers,
but are used to construct applications to talk to OpenStack APIs. Typically
these parts are managed through the `Connection Interface`_, but their use
can be customized.

.. toctree::
   :maxdepth: 1

   resource
   service_description
   utils

Presentations
=============

.. toctree::
   :maxdepth: 1

   multi-cloud-demo
