Connect
=======

In order to work with an OpenStack cloud you first need to create a
:class:`~openstack.connection.Connection` to it using your credentials. A
:class:`~openstack.connection.Connection` can be
created in 3 ways, using the class itself, :ref:`config-clouds-yaml`, or
:ref:`config-environment-variables`. It is recommended to always use
:ref:`config-clouds-yaml` as the same config can be used across tools and
languages.

Create Connection
-----------------

To create a :class:`~openstack.connection.Connection` instance, use the
:func:`~openstack.connect` factory function.

.. literalinclude:: ../examples/connect.py
   :pyobject: create_connection

Full example at `connect.py <http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/examples/connect.py>`_

.. note:: To enable logging, see the :doc:`logging` user guide.

Next
----
Now that you can create a connection, continue with the :ref:`user_guides`
to work with an OpenStack service.

As an alternative to creating a :class:`~openstack.connection.Connection`
using :ref:config-clouds-yaml, you can connect using
`config-environment-variables`.

.. TODO(shade) Update the text here and consolidate with the old
   os-client-config docs so that we have a single and consistent explanation
   of the envvars cloud, etc.
