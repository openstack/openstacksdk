Warnings
========

openstacksdk uses the `warnings`__ infrastructure to warn users about
deprecated resources and resource fields, as well as deprecated behavior in
openstacksdk itself. These warnings are derived from ``Warning`` or
``DeprecationWarning``. In Python, warnings are emitted by default while
deprecation warnings are silenced by default and must be turned on using the
``-Wa`` Python command line option or the ``PYTHONWARNINGS`` environment
variable. If you are writing an application that uses openstacksdk, you may
wish to enable some of these warnings during test runs to ensure you migrate
away from deprecated behavior.

Available warnings
------------------

.. automodule:: openstack.warnings
   :members:

.. __: https://docs.python.org/3/library/warnings.html
