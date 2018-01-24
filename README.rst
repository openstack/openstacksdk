openstacksdk
============

openstacksdk is a client library for for building applications to work
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

A Brief History
---------------

.. TODO(shade) This history section should move to the docs. We can put a
   link to the published URL here in the README, but it's too long.

openstacksdk started its life as three different libraries: shade,
os-client-config and python-openstacksdk.

``shade`` started its life as some code inside of OpenStack Infra's `nodepool`_
project, and as some code inside of the `Ansible OpenStack Modules`_.
Ansible had a bunch of different OpenStack related modules, and there was a
ton of duplicated code. Eventually, between refactoring that duplication into
an internal library, and adding the logic and features that the OpenStack Infra
team had developed to run client applications at scale, it turned out that we'd
written nine-tenths of what we'd need to have a standalone library.

Because of its background from nodepool, shade contained abstractions to
work around deployment differences and is resource oriented rather than service
oriented. This allows a user to think about Security Groups without having to
know whether Security Groups are provided by Nova or Neutron on a given cloud.
On the other hand, as an interface that provides an abstraction, it deviates
from the published OpenStack REST API and adds its own opinions, which may not
get in the way of more advanced users with specific needs.

``os-client-config`` was a library for collecting client configuration for
using an OpenStack cloud in a consistent and comprehensive manner, which
introduced the ``clouds.yaml`` file for expressing named cloud configurations.

``python-openstacksdk`` was a library that exposed the OpenStack APIs to
developers in a consistent and predictable manner.

After a while it became clear that there was value in both the high-level
layer that contains additional business logic and the lower-level SDK that
exposes services and their resources faithfully and consistently as Python
objects.

Even with both of those layers, it is still beneficial at times to be able to
make direct REST calls and to do so with the same properly configured
`Session`_ from `python-requests`_.

This led to the merge of the three projects.

The original contents of the shade library have been moved into
``openstack.cloud`` and os-client-config has been moved in to
``openstack.config``. Future releases of shade will provide a thin
compatibility layer that subclasses the objects from ``openstack.cloud``
and provides different argument defaults where needed for compatibility.
Similarly future releases of os-client-config will provide a compatibility
layer shim around ``openstack.config``.

.. note::

  The ``openstack.cloud.OpenStackCloud`` object and the
  ``openstack.connection.Connection`` object are going to be merged. It is
  recommended to not write any new code which consumes objects from the
  ``openstack.cloud`` namespace until that merge is complete.

.. _nodepool: https://docs.openstack.org/infra/nodepool/
.. _Ansible OpenStack Modules: http://docs.ansible.com/ansible/latest/list_of_cloud_modules.html#openstack
.. _Session: http://docs.python-requests.org/en/master/user/advanced/#session-objects
.. _python-requests: http://docs.python-requests.org/en/master/

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
    openstack.enable_logging(debug=True)

    # Initialize cloud
    # Cloud configs are read with openstack.config
    cloud = openstack.cloud.openstack_cloud(cloud='mordred')

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
