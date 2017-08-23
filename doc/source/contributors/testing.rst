Testing
=======

The tests are run with `tox <https://tox.readthedocs.org/en/latest/>`_ and
configured in ``tox.ini``. The test results are tracked by
`testr <https://testrepository.readthedocs.org/en/latest/>`_ and configured
in ``.testr.conf``.

Unit Tests
----------

Run
***

In order to run the entire unit test suite, simply run the ``tox`` command
inside of your source checkout. This will attempt to run every test command
listed inside of ``tox.ini``, which includes Python 2.7, 3.4, PyPy,
and a PEP 8 check. You should run the full test suite on all versions before
submitting changes for review in order to avoid unexpected failures in the
continuous integration system.::

   (sdk3)$ tox
   ...
   py34: commands succeeded
   py27: commands succeeded
   pypy: commands succeeded
   pep8: commands succeeded
   congratulations :)

During development, it may be more convenient to run a subset of the tests
to keep test time to a minimum. You can choose to run the tests only on one
version. A step further is to run only the tests you are working on.::

   (sdk3)$ tox -e py34                # Run run the tests on Python 3.4
   (sdk3)$ tox -e py34 TestContainer  # Run only the TestContainer tests on 3.4

Functional Tests
----------------

The functional tests assume that you have a public or private OpenStack cloud
that you can run the tests against. The tests must be able to be run against
public clouds but first and foremost they must be run against OpenStack. In
practice, this means that the tests should initially be run against a stable
branch of `DevStack <https://docs.openstack.org/devstack/latest/>`_.

DevStack
********

There are many ways to run and configure DevStack. The link above will show
you how to run DevStack a number of ways. You'll need to choose a method
you're familiar with and can run in your environment. Wherever DevStack is
running, we need to make sure that python-openstacksdk contributors are
using the same configuration.

This is the ``local.conf`` file we use to configure DevStack.

.. literalinclude:: local.conf

Replace ``DEVSTACK_PASSWORD`` with a password of your choice.

Replace ``OPENSTACK_VERSION`` with a `stable branch <http://git.openstack.org/cgit/openstack-dev/devstack/refs/>`_
of OpenStack (without the ``stable/`` prefix on the branch name).

os-client-config
****************

To connect the functional tests to an OpenStack cloud we use
`os-client-config <http://git.openstack.org/cgit/openstack/os-client-config/tree/README.rst>`_.
To setup os-client-config create a ``clouds.yaml`` file in the root of your
source checkout.

This is an example of a minimal configuration for a ``clouds.yaml`` that
connects the functional tests to a DevStack instance. Note that one cloud
under ``clouds`` must be named ``test_cloud``.

.. literalinclude:: clouds.yaml
   :language: yaml

Replace ``xxx.xxx.xxx.xxx`` with the IP address or FQDN of your DevStack
instance.

You can also create a ``~/.config/openstack/clouds.yaml`` file for your
DevStack cloud environment using the following commands. Replace
``DEVSTACK_SOURCE`` with your DevStack source checkout.::

   (sdk3)$ source DEVSTACK_SOURCE/accrc/admin/admin
   (sdk3)$ ./create_yaml.sh

Run
***

Functional tests are run against both Python 2 and 3. In order to run the
entire functional test suite, run the ``tox -e functional`` and
``tox -e functional3`` command inside of your source checkout. This will
attempt to run every test command under ``/openstack/tests/functional/``
in the source tree. You should run the full functional test suite before
submitting changes for review in order to avoid unexpected failures in
the continuous integration system.::

   (sdk3)$ tox -e functional
   ...
   functional: commands succeeded
   congratulations :)
   (sdk3)$ tox -e functional3
   ...
   functional3: commands succeeded
   congratulations :)

Examples Tests
--------------

Similar to the functional tests, the examples tests assume that you have a
public or private OpenStack cloud that you can run the tests against. In
practice, this means that the tests should initially be run against a stable
branch of `DevStack <https://docs.openstack.org/devstack/latest/>`_.
And like the functional tests, the examples tests connect to an OpenStack cloud
using `os-client-config <http://git.openstack.org/cgit/openstack/os-client-config/tree/README.rst>`_.
See the functional tests instructions for information on setting up DevStack
and os-client-config.

Run
***

In order to run the entire examples test suite, simply run the
``tox -e examples`` command inside of your source checkout. This will
attempt to run every test command under ``/openstack/tests/examples/``
in the source tree.::

   (sdk3)$ tox -e examples
   ...
   examples: commands succeeded
   congratulations :)
