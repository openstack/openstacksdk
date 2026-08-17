openstacksdk Style Commandments
===============================

- Step 1: Read the OpenStack Style Commandments
  https://docs.openstack.org/hacking/latest/
- Step 2: Read on

openstacksdk Specific Commandments
----------------------------------

- [O300] ``setUpClass`` not allowed

  ``setUpClass`` looks like it runs once for the class. In parallel test
  execution environments though, it runs once per execution context. This makes
  reasoning about when it is going to actually run and what is going to happen
  extremely difficult and can produce hard to debug test issues.

  Don't ever use it. It makes baby pandas cry.

- [O310] Use of deprecated ``Exception`` class

Linting & Formatting
--------------------

We use `ruff <https://docs.astral.sh/ruff/>`__ in combination with `hacking
<https://docs.openstack.org/hacking/latest/>`__ for linting and formatting.
These can be executed using the ``pep8`` tox target (``tox -e pep8``) or by
installing and running `pre-commit <https://pre-commit.com/>`__.

Unit Tests
----------

Unit tests should be virtually instant. If a unit test takes more than 1 second
to run, it is a bad unit test. Honestly, 1 second is too slow.

All unit test classes should subclass ``openstack.tests.unit.base.TestCase``.
The base ``TestCase`` class takes care of properly creating ``Connection``
objects in a way that protects against local environment.

Test cases should use ``requests-mock`` to mock out HTTP interactions rather
than using mock to mock out object access.

Functional Tests
-----------------

Functional tests run against a live devstack and are slow. Follow these
conventions to keep them fast and reliable.

**One test method per resource.** Each test class should have a single
``test_<resource>`` method that covers the full scenario for that resource
(create, get, list, delete). Prerequisites go in ``setUp``; cleanup goes in
``addCleanup``. This avoids redundant setUp/tearDown cycles and prevents a
failure in one operation from causing knock-on failures in other test methods.

.. code-block:: python

  class TestFlavor(base.BaseFunctionalTest):
      def setUp(self):
          super().setUp()
          # create prerequisites

      def test_flavor(self):
          # create, get, list, update, delete

**Use _delete_foo helpers with addCleanup.** Move resource deletion into a
``_delete_foo`` helper and register it via ``addCleanup`` immediately after
creation. This ensures cleanup runs even if an assertion fails mid-test.

.. code-block:: python

  def _delete_flavor(self, flavor):
      ret = self.admin_compute_client.delete_flavor(flavor)
      self.assertIsNone(ret)

  def test_flavor(self):
      flavor = self.admin_compute_client.create_flavor(...)
      self.addCleanup(self._delete_flavor, flavor)
      # ... remaining assertions

**Fail on misconfigured environments, don't skip.** Tests run against devstack,
not production clouds. If a prerequisite is missing, fail with a descriptive
message rather than silently skipping, so misconfigurations are caught
immediately.

.. code-block:: python

  # Wrong
  if not deployables:
      self.skipTest('No deployables found')

  # Right
  self.assertGreater(
      len(deployables),
      0,
      'no deployables found: is the fake driver enabled?',
  )

**Test both personas where policy differs.** Use ``self.user_cloud`` for
non-admin operations and ``self.operator_cloud`` for admin operations. Where
services enforce different policy rules for admin vs non-admin, test both
personas.

.. code-block:: python

  def test_device_profile(self):
      # get and list as regular user
      ...

  def test_device_profile_admin(self):
      # get, list, and delete as admin
      ...
