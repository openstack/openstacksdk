Connect
=======

In order to work with an OpenStack cloud you first need to create a
:class:`~openstack.connection.Connection` to it using your credentials. A
:class:`~openstack.connection.Connection` can be
created in 3 ways, using the class itself, a file, or environment variables.
If this is your first time using the SDK, we recommend simply using the
class itself as illustrated below.

.. note:: To get your credentials
   `Download the OpenStack RC file <http://docs.openstack.org/cli-reference/content/cli_openrc.html#openrc-dashboard>`_.

Create Connection
-----------------

To create a connection you need a :class:`~openstack.profile.Profile` and a
:class:`~openstack.connection.Connection`.

.. literalinclude:: ../examples/connect.py
   :language: python
   :lines: 32-44

The :class:`~openstack.profile.Profile` sets your preferences for each
service. You will pass it the region of the OpenStack cloud that this
connection will use.

The :class:`~openstack.connection.Connection` is a context for a connection
to an OpenStack cloud. You will primarily use it to set the
:class:`~openstack.profile.Profile` and authentication information with the
``auth_args`` parameter. You can also set the ``user_agent`` to something that
describes your application (e.g. ``my-web-app/1.3.4``).

Full example at `connect.py <http://git.openstack.org/cgit/openstack/python-openstacksdk/tree/examples/connect.py>`_

.. note:: To enable logging, see the :doc:`logging` user guide.

Next
----
Now that you can create a connection, continue with the :ref:`user_guides`
to work with an OpenStack service.

As an alternative to creating a :class:`~openstack.connection.Connection`
using the class itself, you can connect using a file or environment
variables. See the :doc:`connect_from_config` user guide.
