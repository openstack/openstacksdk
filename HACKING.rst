openstacksdk Style Commandments
===============================

Read the OpenStack Style Commandments
https://docs.openstack.org/hacking/latest/

Indentation
-----------

PEP-8 allows for 'visual' indentation. **Do not use it**.
Visual indentation looks like this:

.. code-block:: python

  return_value = self.some_method(arg1, arg1,
                                  arg3, arg4)

Visual indentation makes refactoring the code base unnecessarily hard.

Instead of visual indentation, use this:

.. code-block:: python

  return_value = self.some_method(
      arg1, arg1, arg3, arg4)

That way, if some_method ever needs to be renamed, the only line that needs
to be touched is the line with some_method.

Additionally, if you need to line break at the top of a block, please indent
the continuation line an additional 4 spaces, like this:

.. code-block:: python

  for val in self.some_method(
          arg1, arg1, arg3, arg4):
      self.do_something_awesome()

Neither of these are 'mandated' by PEP-8. However, they are prevailing styles
within this code base.

Unit Tests
----------

Unit tests should be virtually instant. If a unit test takes more than 1 second
to run, it is a bad unit test. Honestly, 1 second is too slow.

All unit test classes should subclass `openstack.tests.unit.base.TestCase`. The
base TestCase class takes care of properly creating `Connection` objects
in a way that protects against local environment.

Test cases should use requests-mock to mock out HTTP interactions rather than
using mock to mock out object access.

Don't Use setUpClass
--------------------

setUpClass looks like it runs once for the class. In parallel test execution
environments though, it runs once per execution context. This makes reasoning
about when it is going to actually run and what is going to happen extremely
difficult and can produce hard to debug test issues.

Don't ever use it. It makes baby pandas cry.
