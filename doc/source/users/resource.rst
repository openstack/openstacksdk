**NOTE: This module is being phased out in favor of**
:mod:`openstack.resource2`. **Once all services have been moved over to use
resource2, that module will take this `resource` name.**

Resource
========
.. automodule:: openstack.resource

The prop class
--------------

.. autoclass:: openstack.resource.prop
   :members:

The Resource class
------------------

.. autoclass:: openstack.resource.Resource
   :members:
   :member-order: bysource

How path_args are used
**********************

As :class:`Resource`\s often contain compound :data:`Resource.base_path`\s,
meaning the path is constructed from more than just that string, the
various request methods need a way to fill in the missing parts.
That's where ``path_args`` come in.

For example::

    class ServerIP(resource.Resource):
        base_path = "/servers/%(server_id)s/ips"

Making a GET request to obtain server IPs requires the ID of the server
to check. This is handled by passing ``{"server_id": "12345"}`` as the
``path_args`` argument when calling :meth:`Resource.get_by_id`. From there,
the method uses Python's string interpolation to fill in the ``server_id``
piece of the URL, and then makes the request.
