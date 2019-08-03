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
write an application that talks to clouds no matter what crazy choices the
deployer has made in an attempt to be more hipster than their self-entitled
narcissist peers, then the Cloud Abstraction layer is for you.

More information about its history can be found at
https://docs.openstack.org/openstacksdk/latest/contributor/history.html

openstack
=========

List servers using objects configured with the ``clouds.yaml`` file:

.. code-block:: python

    import openstack

    # Initialize and turn on debug logging
    openstack.enable_logging(debug=True)

    # Initialize cloud
    conn = openstack.connect(cloud='mordred')

    for server in conn.compute.servers():
        print(server.to_dict())

Cloud Layer
===========

``openstacksdk`` contains a higher-level layer based on logical operations.

.. code-block:: python

    import openstack

    # Initialize and turn on debug logging
    openstack.enable_logging(debug=True)

    for server in conn.list_servers():
        print(server.to_dict())

The benefit is mostly seen in more complicated operations that take multiple
steps and where the steps vary across providers:

.. code-block:: python

    import openstack

    # Initialize and turn on debug logging
    openstack.enable_logging(debug=True)

    # Initialize connection
    # Cloud configs are read with openstack.config
    conn = openstack.connect(cloud='mordred')

    # Upload an image to the cloud
    image = conn.create_image(
        'ubuntu-trusty', filename='ubuntu-trusty.qcow2', wait=True)

    # Find a flavor with at least 512M of RAM
    flavor = conn.get_flavor_by_ram(512)

    # Boot a server, wait for it to boot, and then do whatever is needed
    # to get a public ip for it.
    conn.create_server(
        'my-server', image=image, flavor=flavor, wait=True, auto_ip=True)

openstack.config
================

``openstack.config`` will find cloud configuration for as few as 1 clouds and
as many as you want to put in a config file. It will read environment variables
and config files, and it also contains some vendor specific default values so
that you don't have to know extra info to use OpenStack

* If you have a config file, you will get the clouds listed in it
* If you have environment variables, you will get a cloud named `envvars`
* If you have neither, you will get a cloud named `defaults` with base defaults

Sometimes an example is nice.

Create a ``clouds.yaml`` file:

.. code-block:: yaml

     clouds:
      mordred:
        region_name: Dallas
        auth:
          username: 'mordred'
          password: XXXXXXX
          project_name: 'shade'
          auth_url: 'https://identity.example.com'

Please note: ``openstack.config`` will look for a file called ``clouds.yaml``
in the following locations:

* Current Directory
* ``~/.config/openstack``
* ``/etc/openstack``

More information at https://docs.openstack.org/openstacksdk/latest/user/config/configuration.html

Links
=====

* `Issue Tracker <https://storyboard.openstack.org/#!/project/openstack/openstacksdk>`_
* `Code Review <https://review.opendev.org/#/q/status:open+project:openstack/openstacksdk,n,z>`_
* `Documentation <https://docs.openstack.org/openstacksdk/latest/>`_
* `PyPI <https://pypi.org/project/openstacksdk/>`_
* `Mailing list <http://lists.openstack.org/cgi-bin/mailman/listinfo/openstack-discuss>`_
* `Release Notes <https://docs.openstack.org/releasenotes/openstacksdk>`_
