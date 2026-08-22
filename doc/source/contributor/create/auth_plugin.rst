Creating an Authentication Plugin
=================================

.. note::

   openstacksdk does **not** implement its own authentication plugins. It
   delegates entirely to `keystoneauth1`_. If you want to add a new
   authentication mechanism, you implement it in keystoneauth1, not here. This
   guide explains how openstacksdk *consumes* auth plugins so that you know
   what is required to make a new plugin usable from openstacksdk.

.. _keystoneauth1: https://docs.openstack.org/keystoneauth/latest/

How openstacksdk consumes auth plugins
--------------------------------------

Authentication is configured through the ``auth_type`` and ``auth`` keys of a
cloud's configuration (see :ref:`config-auth-settings`). When a
:class:`~openstack.connection.Connection` is built, openstacksdk resolves and
loads the plugin named by ``auth_type`` using keystoneauth1's loading
machinery. The relevant code lives in ``OpenStackConfig._get_auth_loader`` (in
``openstack/config/loader.py``), which ultimately calls
``keystoneauth1.loading.get_plugin_loader(auth_type)`` and then instantiates
the plugin with ``loader.load_from_options(**auth)``.

A few friendly aliases are handled by openstacksdk before the name is passed to
keystoneauth1 (for example, an empty ``auth_type`` maps to ``none`` and
``token_endpoint`` maps to ``admin_token``), but every real plugin - including
the default, ``password`` - is provided by keystoneauth1. openstacksdk
registers no plugins of its own and ships no ``keystoneauth1.plugin`` entry
points.

Adding a new mechanism
----------------------

Because the loading is entirely delegated, adding a new authentication
mechanism requires **no changes to openstacksdk**. Instead:

#. Implement the plugin and its loader in keystoneauth1, following the
   `keystoneauth plugin documentation
   <https://docs.openstack.org/keystoneauth/latest/authentication-plugins.html>`_.
#. Register it under the ``keystoneauth1.plugin`` entry-point group (this is
   how ``get_plugin_loader`` discovers plugins by name).
#. Once the package providing the plugin is installed alongside openstacksdk,
   it can be selected from ``clouds.yaml`` simply by setting ``auth_type`` to
   your plugin's name, with its options under the ``auth`` key:

   .. code-block:: yaml

       clouds:
         my-cloud:
           auth_type: my-plugin
           auth:
             # options declared by your plugin's loader
             ...

For the full set of authentication options and worked examples of the plugins
that ship with keystoneauth1, see :ref:`config-auth-settings`.
