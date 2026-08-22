Creating a Proxy
================

This guide walks you through adding a *proxy* for a service. It builds on the
:doc:`resource` guide: where a :class:`~openstack.resource.Resource` maps onto
a single server-side resource, a :class:`~openstack.proxy.Proxy` provides the
higher-level, user-facing interface for a whole service. A ``Proxy`` is what a
user reaches through a :class:`~openstack.connection.Connection` - for example,
``conn.compute`` is the compute service's ``Proxy``.

Layout
------

Each service implements a single ``Proxy`` class per API version, in a module
named ``_proxy.py``:

* ``openstack/<service>/v<N>/_proxy.py`` - the proxy, e.g.
  ``openstack/compute/v2/_proxy.py``.
* ``openstack/<service>/v<N>/<resource>.py`` - one module per resource type
  that the proxy operates on, e.g. ``flavor.py``, ``server.py``.

The class is always named ``Proxy`` and subclasses
:class:`openstack.proxy.Proxy`. It declares an ``api_version`` discriminator
and imports each resource module under an underscore-prefixed alias to avoid
namespace collisions:

.. code-block:: python

    from typing import ClassVar, Literal

    from openstack.fake.v2 import fake as _fake
    from openstack import proxy


    class Proxy(proxy.Proxy):
        api_version: ClassVar[Literal['2']] = '2'

Base Helpers
------------

:class:`openstack.proxy.Proxy` subclasses
:class:`keystoneauth1.adapter.Adapter` - so a proxy *is* an authenticated HTTP
client - and adds a set of generic helpers that delegate to the corresponding
methods on your :class:`~openstack.resource.Resource` classes. Each takes the
resource class as its first argument:

``_create``
  Create a resource from keyword attributes.

``_get``
  Fetch a single resource by ID or instance.

``_list``
  Return a generator over resources, with pagination and query filtering.

``_find``
  Look a resource up by name or ID.

``_update``
  Commit changes to a resource.

``_delete``
  Delete a resource.

``_head``
  Issue a ``HEAD`` request for a resource.

``_get_resource``
  Normalize an ID, dict, or existing instance into a ``Resource`` instance.
  Used directly when a method needs an instance to call a resource action on.

Because these helpers do the work, most proxy methods are thin wrappers that
select the right resource class and pass the caller's arguments through.

Methods
-------

Proxy methods follow a consistent naming and shape. A create, get, list, and
delete for a ``Fake`` resource look like this:

.. code-block:: python

    def create_fake(self, **attrs):
        """Create a new fake from attributes

        :param attrs: Keyword arguments which will be used to create a
            :class:`~openstack.fake.v2.fake.Fake`, comprised of the properties
            on the Fake class.

        :returns: The results of fake creation.
        """
        return self._create(_fake.Fake, **attrs)

    def get_fake(self, fake):
        """Get a single fake

        :param fake: The value can be the ID of a fake or a
            :class:`~openstack.fake.v2.fake.Fake` instance.

        :returns: One :class:`~openstack.fake.v2.fake.Fake`
        :raises: :class:`~openstack.exceptions.NotFoundException` when no
            resource can be found.
        """
        return self._get(_fake.Fake, fake)

    def fakes(self, **query):
        """Return a generator of fakes

        :param query: Optional query parameters to be sent to limit the
            resources being returned.

        :returns: A generator of fake objects.
        """
        return self._list(_fake.Fake, **query)

    def delete_fake(self, fake, ignore_missing=True):
        """Delete a fake

        :param fake: The value can be either the ID of a fake or a
            :class:`~openstack.fake.v2.fake.Fake` instance.
        :param ignore_missing: When set to ``False``
            :class:`~openstack.exceptions.NotFoundException` will be raised
            when the fake does not exist. When set to ``True``, no exception
            will be raised when attempting to delete a nonexistent fake.

        :returns: ``None``
        """
        self._delete(_fake.Fake, fake, ignore_missing=ignore_missing)

Note the conventions:

* Methods that accept a resource take "either the ID ... or a
  :class:`~...` instance", and document it that way.
* Deletes and finds take an ``ignore_missing`` argument, defaulting to
  ``True``.
* List methods are named after the plural noun (``fakes``) and return a
  generator; the other methods are named ``<verb>_<resource>``.
* Docstrings use Sphinx field lists (``:param:``, ``:returns:``, ``:raises:``)
  and cross-reference the concrete resource class with ``:class:`~...``` so
  only the short name renders.

For actions that are not simple CRUD, use ``_get_resource`` to obtain an
instance and then call a method on the resource itself.

Wiring the Proxy to a Connection
--------------------------------

A proxy is exposed on the :class:`~openstack.connection.Connection` through a
:class:`~openstack.service_description.ServiceDescription`, as introduced in
the :doc:`resource` guide. The description maps each supported API version to
its proxy class:

.. code-block:: python

    from openstack.fake.v2 import _proxy
    from openstack import service_description


    class FakeService(service_description.ServiceDescription):
        """The fake service."""

        supported_versions = {
            '2': _proxy.Proxy,
        }

Finally, the service must be registered so it becomes an attribute on every
:class:`~openstack.connection.Connection`. The registry lives in the
*generated* file ``openstack/_services_mixin.py``, where each service is
declared with the connection attribute name and its ``service_type``::

    fake = fake_service.FakeService(service_type='fake')

Do not edit ``openstack/_services_mixin.py`` by hand - regenerate it by running
``tools/print-services.py``. Once registered, ``conn.fake`` returns a lazily
constructed instance of your ``Proxy``.
