============
openstacksdk
============

openstacksdk is a client library for building applications to work
with OpenStack clouds. The project aims to provide a consistent and
complete set of interactions with OpenStack's many services, along with
complete documentation, examples, and tools.

It also contains an abstraction interface layer. Clouds can do many things, but
there are probably only about 10 of them that most people care about with any
regularity. If you want to do complicated things, the per-service oriented
portions of the SDK are for you. However, if what you want is to be able to
write an application that talks to any OpenStack cloud regardless of
configuration, then the Cloud Abstraction layer is for you.

More information about the history of openstacksdk can be found at
https://docs.openstack.org/openstacksdk/latest/contributor/history.html

Getting started
---------------

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

openstacksdk will look for ``clouds.yaml`` files in the following locations:

* ``.`` (the current directory)
* ``$HOME/.config/openstack``
* ``/etc/openstack``

openstacksdk consists of three layers. Most users will make use of the *proxy*
layer. Using the above ``clouds.yaml``, consider listing servers:

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

.. _openstack.config:

Configuration
-------------

openstacksdk uses the ``openstack.config`` module to parse configuration.
``openstack.config`` will find cloud configuration for as few as one cloud and
as many as you want to put in a config file. It will read environment variables
and config files, and it also contains some vendor specific default values so
that you don't have to know extra info to use OpenStack

* If you have a config file, you will get the clouds listed in it
* If you have environment variables, you will get a cloud named `envvars`
* If you have neither, you will get a cloud named `defaults` with base defaults

You can view the configuration identified by openstacksdk in your current
environment by running ``openstack.config.loader``. For example:

.. code-block:: bash

   $ python -m openstack.config.loader

More information at https://docs.openstack.org/openstacksdk/latest/user/config/configuration.html

Links
-----

* `Issue Tracker <https://storyboard.openstack.org/#!/project/openstack/openstacksdk>`_
* `Code Review <https://review.opendev.org/#/q/status:open+project:openstack/openstacksdk,n,z>`_
* `Documentation <https://docs.openstack.org/openstacksdk/latest/>`_
* `PyPI <https://pypi.org/project/openstacksdk/>`_
* `Mailing list <http://lists.openstack.org/cgi-bin/mailman/listinfo/openstack-discuss>`_
* `Release Notes <https://docs.openstack.org/releasenotes/openstacksdk>`_
