Testing
=======

The tests are run with `tox <https://tox.readthedocs.org/en/latest/>`_ and
configured in ``tox.ini``. The test results are tracked by
`stestr <https://stestr.readthedocs.io/en/latest/>`_ and configured
in ``.stestr.conf`` and via command line options passed to the ``stestr``
executable when it's called by ``tox``.


Unit Tests
----------

Running tests
~~~~~~~~~~~~~

In order to run the entire unit test suite, simply run the ``tox`` command
inside of your source checkout. This will attempt to run every test command
listed inside of ``tox.ini``, which includes Python 3.x, and a PEP 8 check.
You should run the full test suite on all versions before
submitting changes for review in order to avoid unexpected failures in the
continuous integration system.::

   $ tox
   ...
   py3: commands succeeded
   pep8: commands succeeded
   congratulations :)

During development, it may be more convenient to run a subset of the tests
to keep test time to a minimum. You can choose to run the tests only on one
version. A step further is to run only the tests you are working on.::

   # Run run the tests on Python 3.9
   $ tox -e py39
   # Run only the compute unit tests on Python 3.9
   $ tox -e py39 openstack.tests.unit.compute
   # Run only the tests in a specific file on Python 3.9
   $ tox -e py39 -- -n openstack/tests/unit/compute/test_version.py


Functional Tests
----------------

The functional tests assume that you have a public or private OpenStack cloud
that you can run the tests against. The tests must be able to be run against
public clouds but first and foremost they must be run against OpenStack. In
practice, this means that the tests should initially be run against a stable
branch of `DevStack <https://docs.openstack.org/devstack/latest/>`_.

Configuration
~~~~~~~~~~~~~

To connect the functional tests to an OpenStack cloud we require a
``clouds.yaml`` file, as discussed in :doc:`/user/config/configuration`.
You can place this ``clouds.yaml`` file in the root of your source checkout or
in one of the other standard locations, ``$HOME/.config/openstack`` or
``/etc/openstack``.

There must be at least three clouds configured, or rather three accounts
configured for the one cloud. These accounts are:

- An admin account, which defaults to ``devstack-admin`` but is configurable
  via the ``OPENSTACKSDK_OPERATOR_CLOUD`` environment variable,
- A user account, which defaults to ``devstack`` but is configurable
  via the ``OPENSTACKSDK_DEMO_CLOUD`` environment variable, and
- An alternate user account, which defaults to ``devstack-demo`` but is
  configurable via the ``OPENSTACKSDK_DEMO_CLOUD_ALT`` environment variable

In addition, you must indicate the names of the flavor and image that should be
used for tests. These can be configured via ``OPENSTACKSDK_FLAVOR`` and
``OPENSTACKSDK_IMAGE`` environment variables or ``functional.flavor_name`` and
``functional.image_name`` settings in the ``clouds.yaml`` file, respectively.

Finally, you can configure the timeout for tests using the
``OPENSTACKSDK_FUNC_TEST_TIMEOUT`` environment variable (defaults to 300
seconds). Some test modules take specific timeout values. For example, all
tests in ``openstack.tests.functional.compute`` will check for the
``OPENSTACKSDK_FUNC_TEST_TIMEOUT_COMPUTE`` environment variable before checking
for ``OPENSTACKSDK_FUNC_TEST_TIMEOUT``.

.. note::

    Recent versions of DevStack will configure a suitable ``clouds.yaml`` file
    for you, which will be placed at ``/etc/openstack/clouds.yaml``.

This is an example of a minimal configuration for a ``clouds.yaml`` that
connects the functional tests to a DevStack instance.

.. literalinclude:: clouds.yaml
   :language: yaml

Replace ``xxx.xxx.xxx.xxx`` with the IP address or FQDN of your DevStack
instance.

Running tests
~~~~~~~~~~~~~

Functional tests are also run against multiple Python versions. In order to run
the entire functional test suite against the default Python 3 version in your
environment, run the ``tox -e functional`` command inside of your source
checkout. This will attempt to run every tests in the
``openstack/tests/functional`` directory. For example::

   $ tox -e functional
   ...
   functional: commands succeeded
   congratulations :)
