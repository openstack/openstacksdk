Using OpenStack Key Manager
===========================

Before working with the Key Manager service, you'll need to create a
connection to your OpenStack cloud by following the :doc:`connect` user
guide. This will provide you with the ``conn`` variable used in the examples
below.

.. contents:: Table of Contents
   :local:

.. note:: Some interactions with the Key Manager service differ from that
   of other services in that resources do not have a proper ``id`` parameter,
   which is necessary to make some calls. Instead, resources have a separately
   named id attribute, e.g., the Secret resource has ``secret_id``.

   The examples below outline when to pass in those id values.

Create a Secret
---------------

The Key Manager service allows you to create new secrets by passing the
attributes of the :class:`~openstack.key_manager.v1.secret.Secret` to the
:meth:`~openstack.key_manager.v1._proxy.Proxy.create_secret` method.

.. literalinclude:: ../examples/key_manager/create.py
   :pyobject: create_secret

List Secrets
------------

Once you have stored some secrets, they are available for you to list
via the :meth:`~openstack.key_manager.v1._proxy.Proxy.secrets` method.
This method returns a generator, which yields each
:class:`~openstack.key_manager.v1.secret.Secret`.

.. literalinclude:: ../examples/key_manager/list.py
   :pyobject: list_secrets

The :meth:`~openstack.key_manager.v1._proxy.Proxy.secrets` method can
also make more advanced queries to limit the secrets that are returned.

.. literalinclude:: ../examples/key_manager/list.py
   :pyobject: list_secrets_query

Get Secret Payload
------------------

Once you have received a :class:`~openstack.key_manager.v1.secret.Secret`,
you can obtain the payload for it by passing the secret's id value to
the :meth:`~openstack.key_manager.v1._proxy.Proxy.secrets` method.
Use the :data:`~openstack.key_manager.v1.secret.Secret.secret_id` attribute
when making this request.

.. literalinclude:: ../examples/key_manager/get.py
   :pyobject: get_secret_payload
