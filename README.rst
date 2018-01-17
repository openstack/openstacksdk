openstacksdk
============

openstacksdk is a client library for for building applications to work
with OpenStack clouds. The project aims to provide a consistent and
complete set of interactions with OpenStack's many services, along with
complete documentation, examples, and tools.

It also contains a simple interface layer. Clouds can do many things, but
there are probably only about 10 of them that most people care about with any
regularity. If you want to do complicated things, the per-service oriented
portions of the SDK are for you. However, if what you want is to be able to
write an application that talks to clouds no matter what crazy choices the
deployer has made in an attempt to be more hipster than their self-entitled
narcissist peers, then the ``openstack.cloud`` layer is for you.

A Brief History
---------------

openstacksdk started its life as three different libraries: shade,
os-client-config and python-openstacksdk.

``shade`` started its life as some code inside of OpenStack Infra's nodepool
project, and as some code inside of Ansible. Ansible had a bunch of different
OpenStack related modules, and there was a ton of duplicated code. Eventually,
between refactoring that duplication into an internal library, and adding logic
and features that the OpenStack Infra team had developed to run client
applications at scale, it turned out that we'd written nine-tenths of what we'd
need to have a standalone library.

``os-client-config`` was a library for collecting client configuration for
using an OpenStack cloud in a consistent and comprehensive manner.
In parallel, the python-openstacksdk team was working on a library to expose
the OpenStack APIs to developers in a consistent and predictable manner. After
a while it became clear that there was value in both a high-level layer that
contains business logic, a lower-level SDK that exposes services and their
resources as Python objects, and also to be able to make direct REST calls
when needed with a properly configured Session or Adapter from python-requests.
This led to the merger of the three projects.

The contents of the shade library have been moved into ``openstack.cloud``
and os-client-config has been moved in to ``openstack.config``. The next
release of shade will be a thin compatibility layer that subclasses the objects
from ``openstack.cloud`` and provides different argument defaults where needed
for compat. Similarly the next release of os-client-config will be a compat
layer shim around ``openstack.config``.

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

More information at https://developer.openstack.org/sdks/python/openstacksdk/users/config

openstack.cloud
===============

Create a server using objects configured with the ``clouds.yaml`` file:

.. code-block:: python

    import openstack.cloud

    # Initialize and turn on debug logging
    openstack.cloud.simple_logging(debug=True)

    # Initialize cloud
    # Cloud configs are read with openstack.config
    cloud = openstack.openstack_cloud(cloud='mordred')

    # Upload an image to the cloud
    image = cloud.create_image(
        'ubuntu-trusty', filename='ubuntu-trusty.qcow2', wait=True)

    # Find a flavor with at least 512M of RAM
    flavor = cloud.get_flavor_by_ram(512)

    # Boot a server, wait for it to boot, and then do whatever is needed
    # to get a public ip for it.
    cloud.create_server(
        'my-server', image=image, flavor=flavor, wait=True, auto_ip=True)

Links
=====

* `Issue Tracker <https://storyboard.openstack.org/#!/project/760>`_
* `Code Review <https://review.openstack.org/#/q/status:open+project:openstack/python-openstacksdk,n,z>`_
* `Documentation <https://developer.openstack.org/sdks/python/openstacksdk/>`_
* `PyPI <https://pypi.python.org/pypi/python-openstacksdk/>`_
* `Mailing list <http://lists.openstack.org/cgi-bin/mailman/listinfo/openstack-dev>`_
* `Bugs <https://bugs.launchpad.net/python-openstacksdk>`_
