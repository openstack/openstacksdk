Getting started with the OpenStack SDK
======================================

For a listing of terms used throughout the SDK, including the names of
projects and services supported by it, see the :doc:`glossary <../glossary>`.

Installation
------------

The OpenStack SDK is available on
`PyPI <https://pypi.python.org/pypi/openstacksdk>`_ under the name
**openstacksdk**. To install it, use ``pip``::

   $ pip install openstacksdk

.. _user_guides:

User Guides
-----------

These guides walk you through how to make use of the libraries we provide
to work with each OpenStack service. If you're looking for a cookbook
approach, this is where you'll want to begin.

.. toctree::
   :maxdepth: 1

   Connect to an OpenStack Cloud <guides/connect>
   Connect to an OpenStack Cloud Using a Config File <guides/connect_from_config>
   Logging <guides/logging>
   Block Store <guides/block_store>
   Cluster <guides/cluster>
   Compute <guides/compute>
   Database <guides/database>
   Identity <guides/identity>
   Image <guides/image>
   Key Manager <guides/key_manager>
   Network <guides/network>
   Object Store <guides/object_store>
   Orchestration <guides/orchestration>
   Telemetry <guides/telemetry>

API Documentation
-----------------

Service APIs are exposed through a two-layered approach. The classes
exposed through our *Connection* interface are the place to start if you're
an application developer consuming an OpenStack cloud. The *Resource*
interface is the layer upon which the *Connection* is built, with
*Connection* methods accepting and returning *Resource* objects.

Connection Interface
********************

A *Connection* instance maintains your session, authentication, transport,
and profile, providing you with a set of higher-level interfaces to work
with OpenStack services.

.. toctree::
   :maxdepth: 1

   connection
   profile

Once you have a *Connection* instance, the following services may be exposed
to you. Your user profile determine the full set of exposed services,
but listed below are the ones provided by this SDK by default.

.. toctree::
   :maxdepth: 1

   Block Store <proxies/block_store>
   Cluster <proxies/cluster>
   Compute <proxies/compute>
   Database <proxies/database>
   Identity <proxies/identity>
   Image <proxies/image>
   Key Manager <proxies/key_manager>
   Network <proxies/network>
   Object Store <proxies/object_store>
   Orchestration <proxies/orchestration>
   Telemetry <proxies/telemetry>

Resource Interface
******************

The *Resource* layer is a lower-level interface to communicate with OpenStack
services. While the classes exposed by the *Connection* build a convenience
layer on top of this, *Resources* can be used directly. However, the most
common usage of this layer is in receiving an object from a class in the
*Connection* layer, modifying it, and sending it back into the *Connection*
layer, such as to update a resource on the server.

The following services have exposed *Resource* classes.

.. toctree::
   :maxdepth: 1

   Block Store <resources/block_store/index>
   Cluster <resources/cluster/index>
   Compute <resources/compute/index>
   Database <resources/database/index>
   Identity <resources/identity/index>
   Image <resources/image/index>
   Key Management <resources/key_manager/index>
   Metric <resources/metric/index>
   Network <resources/network/index>
   Orchestration <resources/orchestration/index>
   Object Store <resources/object_store/index>
   Telemetry <resources/telemetry/index>

Low-Level Classes
*****************

The following classes are not commonly used by application developers,
but are used to construct applications to talk to OpenStack APIs. Typically
these parts are managed through the `Connection Interface`_, but their use
can be customized.

.. toctree::
   :maxdepth: 1

   session
   resource
   service_filter
   utils
