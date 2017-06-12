OpenStack Python SDK
====================

The ``python-openstacksdk`` is a collection of libraries for building
applications to work with OpenStack clouds. The project aims to provide
a consistent and complete set of interactions with OpenStack's many
services, along with complete documentation, examples, and tools.

This SDK is under active development, and in the interests of providing
a high-quality interface, the APIs provided in this release may differ
from those provided in future release.

Usage
-----

The following example simply connects to an OpenStack cloud and lists
the containers in the Object Store service.::

   from openstack import connection
   conn = connection.Connection(auth_url="http://openstack:5000/v3",
                                project_name="big_project",
                                username="SDK_user",
                                password="Super5ecretPassw0rd")
   for container in conn.object_store.containers():
      print(container.name)

Documentation
-------------

Documentation is available at
http://developer.openstack.org/sdks/python/openstacksdk/

License
-------

Apache 2.0
