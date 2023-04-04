Warnings
========

openstacksdk uses the `warnings`__ infrastructure to warn users about
deprecated resources and resource fields, as well as deprecated behavior in
openstacksdk itself. Currently, these warnings are all derived from
``DeprecationWarning``. In Python, deprecation warnings are silenced by
default. You must turn them on using the ``-Wa`` Python command line option or
the ``PYTHONWARNINGS`` environment variable. If you are writing an application
that uses openstacksdk, you may wish to enable some of these warnings during
test runs to ensure you migrate away from deprecated behavior.

Available warnings
------------------

.. automodule:: openstack.warnings

.. __: https://docs.python.org/3/library/warnings.html
