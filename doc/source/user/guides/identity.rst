Using OpenStack Identity
========================

Before working with the Identity service, you'll need to create a connection
to your OpenStack cloud by following the :doc:`connect` user guide. This will
provide you with the ``conn`` variable used in the examples below.

The OpenStack Identity service is the default identity management system for
OpenStack. The Identity service authentication process confirms the identity
of a user and an incoming request by validating a set of credentials that the
user supplies. Initially, these credentials are a user name and password or a
user name and API key. When the Identity service validates user credentials,
it issues an authentication token that the user provides in subsequent
requests. An authentication token is an alpha-numeric text string that enables
access to OpenStack APIs and resources. A token may be revoked at any time and
is valid for a finite duration.

List Users
----------
A **user** is a digital representation of a person, system, or service that
uses OpenStack cloud services. The Identity service validates that incoming
requests are made by the user who claims to be making the call. Users have
a login and can access resources by using assigned tokens. Users can be
directly assigned to a particular project and behave as if they are contained
in that project.

.. literalinclude:: ../examples/identity/list.py
   :pyobject: list_users

Full example: `identity resource list`_

List Credentials
----------------
**Credentials** are data that confirms the identity of the user. For example,
user name and password, user name and API key, or an authentication token that
the Identity service provides.

.. literalinclude:: ../examples/identity/list.py
   :pyobject: list_credentials

Full example: `identity resource list`_

List Projects
-------------
A **project** is a container that groups or isolates resources or identity
objects.

.. literalinclude:: ../examples/identity/list.py
   :pyobject: list_projects

Full example: `identity resource list`_

List Domains
------------
A **domain** is an Identity service API v3 entity and represents a collection
of projects and users that defines administrative boundaries for the management
of Identity entities. Users can be granted the administrator role for a domain.
A domain administrator can create projects, users, and groups in a domain and
assign roles to users and groups in a domain.

.. literalinclude:: ../examples/identity/list.py
   :pyobject: list_domains

Full example: `identity resource list`_

List Groups
-----------
A **group** is an Identity service API v3 entity and represents a collection of
users that are owned by a domain. A group role granted to a domain or project
applies to all users in the group. Adding users to, or removing users from, a
group respectively grants, or revokes, their role and authentication to the
associated domain or project.

.. literalinclude:: ../examples/identity/list.py
   :pyobject: list_groups

Full example: `identity resource list`_

List Services
-------------
A **service** is an OpenStack service, such as Compute, Object Storage, or
Image service, that provides one or more endpoints through which users can
access resources and perform operations.

.. literalinclude:: ../examples/identity/list.py
   :pyobject: list_services

Full example: `identity resource list`_

List Endpoints
--------------
An **endpoint** is a network-accessible address, usually a URL, through which
you can access a service.

.. literalinclude:: ../examples/identity/list.py
   :pyobject: list_endpoints

Full example: `identity resource list`_

List Regions
------------
A **region** is an Identity service API v3 entity and represents a general
division in an OpenStack deployment. You can associate zero or more
sub-regions with a region to make a tree-like structured hierarchy.

.. literalinclude:: ../examples/identity/list.py
   :pyobject: list_regions

Full example: `identity resource list`_

.. _identity resource list: https://opendev.org/openstack/openstacksdk/src/branch/master/examples/identity/list.py
