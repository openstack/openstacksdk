==============
Service Tokens
==============

When OpenStack services communicate with each other on behalf of a user - such
as the Compute service (Nova) calling the Block Storage service (Cinder) or
Networking service (Neutron) - operations can fail if the user's authentication
token expires before the multi-step operation finishes.

To solve this problem, OpenStack supports **service tokens**. A service token
is a secondary token issued to a dedicated service account and transmitted via
the ``X-Service-Token`` HTTP header alongside the primary user's
``X-Auth-Token`` header.

When the receiving service (such as Cinder) receives both tokens, its
`keystonemiddleware`_ pipeline validates the service token. If the service
token is valid, the operation is permitted to proceed even if the user's token
has expired, provided the operation was initiated while the user's token was
valid. Service tokens also allow target services to verify the identity of the
calling service and authorize service-specific roles.

For a detailed explanation of service users and tokens in OpenStack, see the
`Keystone documentation on managing service users`__.

.. _keystonemiddleware: https://docs.openstack.org/keystonemiddleware/latest/
.. __: https://docs.openstack.org/keystone/latest/admin/manage-services.html

Using service tokens with openstacksdk
--------------------------------------

`openstacksdk` relies on `keystoneauth`_ for HTTP communication and session
management. To attach a service token to requests made by an SDK
:class:`~openstack.connection.Connection`, you configure a
:class:`keystoneauth1.service_token.ServiceTokenAuthWrapper`.

The wrapper combines two distinct authentication plugins:

* **User Authentication Plugin** (``user_auth``): Provides credentials for the
  initiating user or the calling service's standard user context (sent in the
  ``X-Auth-Token`` header).

* **Service Authentication Plugin** (``service_auth``): Provides credentials
  for the service user account (sent in the ``X-Service-Token`` header).

Once wrapped, the composite auth plugin is passed to a
:class:`keystoneauth1.session.Session`, which is then supplied to the SDK
:class:`~openstack.connection.Connection` constructor:

.. code-block:: python

    from keystoneauth1 import service_token
    from keystoneauth1 import session as ks_session
    import openstack.connection

    auth = service_token.ServiceTokenAuthWrapper(
        user_auth=user_auth,
        service_auth=service_auth,
    )
    sess = ks_session.Session(auth=auth)
    conn = openstack.connection.Connection(session=sess, region_name=region)

Configuration
-------------

There are two primary mechanisms available for configuring service tokens.

Service user auth with a service token (oslo.config)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In an OpenStack service operational context (such as Nova communicating with
Cinder), configuration is typically managed via `oslo.config`_.

The service configuration file defines credentials for both the target service
client group (e.g. ``[cinder]``) and the service user group
(``[service_user]``):

.. code-block:: ini

    [cinder]
    auth_type = password
    auth_url = https://identity.example.com/identity/v3
    project_domain_name = Default
    project_name = service
    user_domain_name = Default
    username = nova
    password = secret-nova-password
    os_region_name = RegionOne

    [service_user]
    send_service_user_token = true
    auth_type = password
    auth_url = https://identity.example.com/identity/v3
    project_domain_name = Default
    project_name = service
    user_domain_name = Default
    username = nova
    password = secret-nova-password

Both plugins are loaded using :mod:`keystoneauth1.loading` and wrapped
together:

.. code-block:: python

    from keystoneauth1 import loading as ks_loading
    from keystoneauth1 import service_token
    from keystoneauth1 import session as ks_session
    import openstack.connection
    from oslo_config import cfg

    CONF = cfg.CONF

    # Load target service auth and service token auth
    cinder_auth = ks_loading.load_auth_from_conf_options(CONF, 'cinder')
    service_auth = ks_loading.load_auth_from_conf_options(CONF, 'service_user')

    # Wrap them so both tokens are sent
    auth = service_token.ServiceTokenAuthWrapper(
        user_auth=cinder_auth,
        service_auth=service_auth,
    )
    sess = ks_session.Session(auth=auth)

    conn = openstack.connection.Connection(
        session=sess,
        region_name=CONF.cinder.os_region_name,
    )

End-user credentials with a service token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When an operation is initiated by an end user whose credentials are loaded from
a standard ``clouds.yaml`` configuration (or an incoming request context), but
the application must include a service token from its configuration file, you
can combine the two sources:

.. code-block:: python

    import os
    from keystoneauth1 import loading as ks_loading
    from keystoneauth1 import service_token
    from keystoneauth1 import session as ks_session
    import openstack.config
    import openstack.connection
    from oslo_config import cfg

    CONF = cfg.CONF

    # User credentials from clouds.yaml
    cloud_config = openstack.config.OpenStackConfig().get_one(
        cloud=os.environ['OS_CLOUD']
    )
    user_auth = cloud_config.get_auth()

    # Service token credentials from service configuration
    service_auth = ks_loading.load_auth_from_conf_options(CONF, 'service_user')

    auth = service_token.ServiceTokenAuthWrapper(
        user_auth=user_auth,
        service_auth=service_auth,
    )
    sess = ks_session.Session(auth=auth)

    conn = openstack.connection.Connection(
        session=sess,
        region_name=CONF.cinder.os_region_name,
    )

Example
-------

A full runnable script demonstrating this pattern against Cinder's
list-volume-types endpoint is available in the repository at
``examples/advanced/service_tokens.py``:

.. literalinclude:: examples/advanced/service_tokens.py
   :language: python

To test this locally with an HTTP proxy (such as mitmproxy) to inspect the
outgoing ``X-Auth-Token`` and ``X-Service-Token`` headers:

.. code-block:: bash

    export HTTP_PROXY=http://127.0.0.1:8080
    python examples/advanced/service_tokens.py

.. _keystoneauth: https://docs.openstack.org/keystoneauth/latest/
.. _oslo.config: https://docs.openstack.org/oslo.config/latest/
