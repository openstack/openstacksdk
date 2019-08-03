A Brief History
===============

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
``openstack.config``.

.. _nodepool: https://docs.openstack.org/infra/nodepool/
.. _Ansible OpenStack Modules: http://docs.ansible.com/ansible/latest/list_of_cloud_modules.html#openstack
.. _Session: http://docs.python-requests.org/en/master/user/advanced/#session-objects
.. _python-requests: http://docs.python-requests.org/en/master/
