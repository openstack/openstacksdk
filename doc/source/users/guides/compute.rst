Using OpenStack Compute
=======================

Before working with the Compute service, you'll need to create a connection
to your OpenStack cloud by following the :doc:`connect` user guide. This will
provide you with the ``conn`` variable used in the examples below.

.. contents:: Table of Contents
   :local:

The primary resource of the Compute service is the server.

List Servers
------------

A **server** is a virtual machine that provides access to a compute instance
being run by your cloud provider.

.. literalinclude:: ../examples/compute/list.py
   :pyobject: list_servers

Full example: `compute resource list`_

List Images
-----------

An **image** is the operating system you want to use for your server.

.. literalinclude:: ../examples/compute/list.py
   :pyobject: list_images

Full example: `compute resource list`_

List Flavors
------------

A **flavor** is the resource configuration for a server. Each flavor is a
unique combination of disk, memory, vCPUs, and network bandwidth.

.. literalinclude:: ../examples/compute/list.py
   :pyobject: list_flavors

Full example: `compute resource list`_

List Networks
-------------

A **network** provides connectivity to servers.

.. literalinclude:: ../examples/network/list.py
   :pyobject: list_networks

Full example: `network resource list`_

Create Key Pair
---------------

A **key pair** is the public key and private key of
`public–key cryptography`_. They are used to encrypt and decrypt login
information when connecting to your server.

.. literalinclude:: ../examples/compute/create.py
   :pyobject: create_keypair

Full example: `compute resource create`_

Create Server
-------------

At minimum, a server requires a name, an image, a flavor, and a network on
creation. You can discover the names and IDs of these attributes by listing
them as above and then using the find methods to get the appropriate
resources.

Ideally you'll also create a server using a keypair so you can login to that
server with the private key.

Servers take time to boot so we call ``wait_for_server`` to wait
for it to become active.

.. literalinclude:: ../examples/compute/create.py
   :pyobject: create_server

Full example: `compute resource create`_

.. _compute resource list: http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/examples/compute/list.py
.. _network resource list: http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/examples/network/list.py
.. _compute resource create: http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/examples/compute/create.py
.. _public–key cryptography: https://en.wikipedia.org/wiki/Public-key_cryptography