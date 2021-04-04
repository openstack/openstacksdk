===============
Getting started
===============

openstacksdk aims to talk to any OpenStack cloud. To do this, it requires a
configuration file. openstacksdk favours ``clouds.yaml`` files, but can also
use environment variables. The ``clouds.yaml`` file should be provided by your
cloud provider or deployment tooling. An example:

.. code-block:: yaml

    clouds:
     mordred:
       region_name: Dallas
       auth:
         username: 'mordred'
         password: XXXXXXX
         project_name: 'demo'
         auth_url: 'https://identity.example.com'

More information on configuring openstacksdk can be found in
:doc:`/user/config/configuration`.

Given sufficient configuration, you can use openstacksdk to interact with your
cloud. openstacksdk consists of three layers. Most users will make use of the
*proxy* layer. Using the above ``clouds.yaml``, consider listing servers:

.. code-block:: python

    import openstack

    # Initialize and turn on debug logging
    openstack.enable_logging(debug=True)

    # Initialize connection
    conn = openstack.connect(cloud='mordred')

    # List the servers
    for server in conn.compute.servers():
        print(server.to_dict())

openstacksdk also contains a higher-level *cloud* layer based on logical
operations:

.. code-block:: python

    import openstack

    # Initialize and turn on debug logging
    openstack.enable_logging(debug=True)

    # Initialize connection
    conn = openstack.connect(cloud='mordred')

    # List the servers
    for server in conn.list_servers():
        print(server.to_dict())

The benefit of this layer is mostly seen in more complicated operations that
take multiple steps and where the steps vary across providers. For example:

.. code-block:: python

    import openstack

    # Initialize and turn on debug logging
    openstack.enable_logging(debug=True)

    # Initialize connection
    conn = openstack.connect(cloud='mordred')

    # Upload an image to the cloud
    image = conn.create_image(
        'ubuntu-trusty', filename='ubuntu-trusty.qcow2', wait=True)

    # Find a flavor with at least 512M of RAM
    flavor = conn.get_flavor_by_ram(512)

    # Boot a server, wait for it to boot, and then do whatever is needed
    # to get a public IP address for it.
    conn.create_server(
        'my-server', image=image, flavor=flavor, wait=True, auto_ip=True)

Finally, there is the low-level *resource* layer. This provides support for the
basic CRUD operations supported by REST APIs and is the base building block for
the other layers. You typically will not need to use this directly:

.. code-block:: python

    import openstack
    import openstack.config.loader
    import openstack.compute.v2.server

    # Initialize and turn on debug logging
    openstack.enable_logging(debug=True)

    # Initialize connection
    conn = openstack.connect(cloud='mordred')

    # List the servers
    for server in openstack.compute.v2.server.Server.list(session=conn.compute):
        print(server.to_dict())
