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

.. rubric:: Authentication and connection management

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

* If set, the path indicated by the ``OS_CLIENT_CONFIG_FILE`` environment
  variable
* ``.`` (the current directory)
* ``$HOME/.config/openstack``
* ``/etc/openstack``

You can create a connection using the ``openstack.connect`` function. The cloud
name can be either passed directly to this function or specified using the
``OS_CLOUD`` environment variable. If you don't have a ``clouds.yaml`` file and
instead use environment variables for configuration then you can use the
special ``envvars`` cloud name to load configuration from the environment. For
example:

.. code-block:: python

    import openstack

    # Initialize connection from a clouds.yaml by passing a cloud name
    conn_from_cloud_name = openstack.connect(cloud='mordred')

    # Initialize connection from a clouds.yaml using the OS_CLOUD envvar
    conn_from_os_cloud = openstack.connect()

    # Initialize connection from environment variables
    conn_from_env_vars = openstack.connect(cloud='envvars')

.. note::

    How this is all achieved is described in more detail `below
    <openstack.config>`__.

.. rubric:: The cloud layer

openstacksdk consists of four layers which all build on top of each other. The
highest level layer is the *cloud* layer. Cloud layer methods are available via
the top level ``Connection`` object returned by ``openstack.connect``. For
example:

.. code-block:: python

    import openstack

    # Initialize and turn on debug logging
    openstack.enable_logging(debug=True)

    # Initialize connection
    conn = openstack.connect(cloud='mordred')

    # List the servers
    for server in conn.list_servers():
        print(server.to_dict())

The cloud layer is based on logical operations that can potentially touch
multiple services. The benefit of this layer is mostly seen in more complicated
operations that take multiple steps and where the steps vary across providers.
For example:

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

.. rubric:: The proxy layer

The next layer is the *proxy* layer. Most users will make use of this layer.
The proxy layer is service-specific, so methods will be available under
service-specific connection attributes of the ``Connection`` object such as
``compute``, ``block_storage``, ``image`` etc. For example:

.. code-block:: python

    import openstack

    # Initialize and turn on debug logging
    openstack.enable_logging(debug=True)

    # Initialize connection
    conn = openstack.connect(cloud='mordred')

    # List the servers
    for server in conn.compute.servers():
        print(server.to_dict())

.. note::

    A list of supported services is given `below <supported-services>`__.

.. rubric:: The resource layer

Below this there is the *resource* layer. This provides support for the basic
CRUD operations supported by REST APIs and is the base building block for the
other layers. You typically will not need to use this directly but it can be
helpful for operations where you already have a ``Resource`` object to hand.
For example:

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

.. rubric:: The raw HTTP layer

Finally, there is the *raw HTTP* layer. This exposes raw HTTP semantics and
is effectively a wrapper around the `requests`__ API with added smarts to
handle stuff like authentication and version management. As such, you can use
the ``requests`` API methods you know and love, like ``get``, ``post`` and
``put``, and expect to receive a ``requests.Response`` object in response
(unlike the other layers, which mostly all return objects that subclass
``openstack.resource.Resource``). Like the *resource* layer, you will typically
not need to use this directly but it can be helpful to interact with APIs that
have not or will not be supported by openstacksdk. For example:

.. code-block:: python

    import openstack

    # Initialize and turn on debug logging
    openstack.enable_logging(debug=True)

    # Initialize connection
    conn = openstack.connect(cloud='mordred')

    # List servers
    for server in openstack.compute.get('/servers').json():
        print(server)

.. __: https://requests.readthedocs.io/en/latest/

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

.. _supported-services:

Supported services
------------------

The following services are currently supported. A full list of all available
OpenStack service can be found in the `Project Navigator`__.

.. note::

   Support here does not guarantee full-support for all APIs. It simply means
   some aspect of the project is supported.

.. list-table:: Supported services
   :widths: 15 25 10 40
   :header-rows: 1

   * - Service
     - Description
     - Cloud Layer
     - Proxy & Resource Layer

   * - **Compute**
     -
     -
     -

   * - Nova
     - Compute
     - ✔
     - ✔ (``openstack.compute``)

   * - **Hardware Lifecycle**
     -
     -
     -

   * - Ironic
     - Bare metal provisioning
     - ✔
     - ✔ (``openstack.baremetal``, ``openstack.baremetal_introspection``)

   * - Cyborg
     - Lifecycle management of accelerators
     - ✔
     - ✔ (``openstack.accelerator``)

   * - **Storage**
     -
     -
     -

   * - Cinder
     - Block storage
     - ✔
     - ✔ (``openstack.block_storage``)

   * - Swift
     - Object store
     - ✔
     - ✔ (``openstack.object_store``)

   * - Cinder
     - Shared filesystems
     - ✔
     - ✔ (``openstack.shared_file_system``)

   * - **Networking**
     -
     -
     -

   * - Neutron
     - Networking
     - ✔
     - ✔ (``openstack.network``)

   * - Octavia
     - Load balancing
     - ✔
     - ✔ (``openstack.load_balancer``)

   * - Designate
     - DNS
     - ✔
     - ✔ (``openstack.dns``)

   * - **Shared services**
     -
     -
     -

   * - Keystone
     - Identity
     - ✔
     - ✔ (``openstack.identity``)

   * - Placement
     - Placement
     - ✔
     - ✔ (``openstack.placement``)

   * - Glance
     - Image storage
     - ✔
     - ✔ (``openstack.image``)

   * - Barbican
     - Key management
     - ✔
     - ✔ (``openstack.key_manager``)

   * - **Workload provisioning**
     -
     -
     -

   * - Magnum
     - Container orchestration engine provisioning
     - ✔
     - ✔ (``openstack.container_infrastructure_management``)

   * - **Orchestration**
     -
     -
     -

   * - Heat
     - Orchestration
     - ✔
     - ✔ (``openstack.orchestration``)

   * - Senlin
     - Clustering
     - ✔
     - ✔ (``openstack.clustering``)

   * - Mistral
     - Workflow
     - ✔
     - ✔ (``openstack.workflow``)

   * - Zaqar
     - Messaging
     - ✔
     - ✔ (``openstack.message``)

   * - **Application lifecycle**
     -
     -
     -

   * - Masakari
     - Instances high availability service
     - ✔
     - ✔ (``openstack.instance_ha``)

.. __: https://www.openstack.org/software/project-navigator/openstack-components#openstack-services

Links
-----

* `Issue Tracker <https://bugs.launchpad.net/openstacksdk>`_
* `Code Review <https://review.opendev.org/#/q/status:open+project:openstack/openstacksdk,n,z>`_
* `Documentation <https://docs.openstack.org/openstacksdk/latest/>`_
* `PyPI <https://pypi.org/project/openstacksdk/>`_
* `Mailing list <https://lists.openstack.org/mailman3/lists/openstack-discuss.lists.openstack.org/>`_
* `Release Notes <https://docs.openstack.org/releasenotes/openstacksdk>`_
