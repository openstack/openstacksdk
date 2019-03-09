How the SDK is organized
========================

The following diagram shows how the project is laid out.

.. literalinclude:: layout.txt

Resource
--------

The :class:`openstack.resource.Resource` base class is the building block
of any service implementation. ``Resource`` objects correspond to the
resources each service's REST API works with, so the
:class:`openstack.compute.v2.server.Server` subclass maps to the compute
service's ``https://openstack:1234/v2/servers`` resource.

The base ``Resource`` contains methods to support the typical
`CRUD <http://en.wikipedia.org/wiki/Create,_read,_update_and_delete>`_
operations supported by REST APIs, and handles the construction of URLs
and calling the appropriate HTTP verb on the given ``Adapter``.

Values sent to or returned from the service are implemented as attributes
on the ``Resource`` subclass with type :class:`openstack.resource.prop`.
The ``prop`` is created with the exact name of what the API expects,
and can optionally include a ``type`` to be validated against on requests.
You should choose an attribute name that follows PEP-8, regardless of what
the server-side expects, as this ``prop`` becomes a mapping between the two.::

   is_public = resource.prop('os-flavor-access:is_public', type=bool)

There are six additional attributes which the ``Resource`` class checks
before making requests to the REST API. ``allow_create``, ``allow_retreive``,
``allow_commit``, ``allow_delete``, ``allow_head``, and ``allow_list`` are set
to ``True`` or ``False``, and are checked before making the corresponding
method call.

The ``base_path`` attribute should be set to the URL which corresponds to
this resource. Many ``base_path``\s are simple, such as ``"/servers"``.
For ``base_path``\s which are composed of non-static information, Python's
string replacement is used, e.g., ``base_path = "/servers/%(server_id)s/ips"``.

``resource_key`` and ``resources_key`` are attributes to set when a
``Resource`` returns more than one item in a response, or otherwise
requires a key to obtain the response value. For example, the ``Server``
class sets ``resource_key = "server"`` as an individual ``Server`` is
stored in a dictionary keyed with the singular noun,
and ``resource_keys = "servers"`` as multiple ``Server``\s are stored in
a dictionary keyed with the plural noun in the response.

Proxy
-----

Each service implements a ``Proxy`` class based on
:class:`~openstack.proxy.Proxy`, within the
``openstack/<program_name>/vX/_proxy.py`` module. For example, the v2 compute
service's ``Proxy`` exists in ``openstack/compute/v2/_proxy.py``.

The :class:`~openstack.proxy.Proxy` class is based on
:class:`~keystoneauth1.adapter.Adapter`.

.. autoclass:: openstack.proxy.Proxy
   :members:
   :show-inheritance:

Each service's ``Proxy`` provides a higher-level interface for users to work
with via a :class:`~openstack.connection.Connection` instance.

Rather than requiring users to maintain their own ``Adapter`` and work with
lower-level :class:`~openstack.resource.Resource` objects, the ``Proxy``
interface offers a place to make things easier for the caller.

Each ``Proxy`` class implements methods which act on the underlying
``Resource`` classes which represent the service. For example::

   def list_flavors(self, **params):
       return flavor.Flavor.list(self.session, **params)

This method is operating on the ``openstack.compute.v2.flavor.Flavor.list``
method. For the time being, it simply passes on the ``Adapter`` maintained
by the ``Proxy``, and returns what the underlying ``Resource.list`` method
does.

The implementations and method signatures of ``Proxy`` methods are currently
under construction, as we figure out the best way to implement them in a
way which will apply nicely across all of the services.

Connection
----------

The :class:`openstack.connection.Connection` class builds atop a
:class:`openstack.config.cloud_region.CloudRegion` object, and provides a
higher level interface constructed of ``Proxy`` objects from each of the
services.

The ``Connection`` class' primary purpose is to act as a high-level interface
to this SDK, managing the lower level connecton bits and exposing the
``Resource`` objects through their corresponding `Proxy`_ object.

If you've built proper ``Resource`` objects and implemented methods on the
corresponding ``Proxy`` object, the high-level interface to your service
should now be exposed.
