Creating a New Resource
=======================

This guide will walk you through how to add resources for a service.

Naming Conventions
------------------

Above all, names across this project conform to Python's naming standards,
as laid out in `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_.

The relevant details we need to know are as follows:

   * Module names are lower case, and separated by underscores if more than
     one word. For example, ``openstack.object_store``
   * Class names are capitalized, with no spacing, and each subsequent word is
     capitalized in a name. For example, ``ServerMetadata``.
   * Attributes on classes, including methods, are lower case and separated
     by underscores. For example, ``allow_list`` or ``get_data``.

Services
********

Services in the OpenStack SDK are named after their program name, not their
code name. For example, the project often known as "Nova" is always called
"compute" within this SDK.

This guide walks through creating service for an OpenStack program called
"Fake". Following our guidelines, the code for its service would
live under the ``openstack.fake`` namespace. What follows is the creation
of a :class:`~openstack.resource.Resource` class for the "Fake" service.

Resources
*********

Resources are named after the server-side resource, which is set in the
``base_path`` attribute of the resource class. This guide creates a
resource class for the ``/fake`` server resource, so the resource module
is called ``fake.py`` and the class is called ``Fake``.

An Example
----------

``openstack/fake/fake_service.py``

.. literalinclude:: examples/resource/fake_service.py
   :language: Python
   :linenos:

``openstack/fake/v2/fake.py``

.. literalinclude:: examples/resource/fake.py
   :language: Python
   :linenos:

``fake.Fake`` Attributes
------------------------

Each service's resources inherit from :class:`~openstack.resource.Resource`,
so they can override any of the base attributes to fit the way their
particular resource operates.

``resource_key`` and ``resources_key``
**************************************

These attributes are set based on how your resource responds with data.
The default values for each of these are ``None``, which works fine
when your resource returns a JSON body that can be used directly without a
top-level key, such as ``{"name": "Ernie Banks", ...}"``.

However, our ``Fake`` resource returns JSON bodies that have the details of
the resource one level deeper, such as
``{"resources": {"name": "Ernie Banks", ...}, {...}}``. It does a similar
thing with single resources, putting them inside a dictionary keyed on
``"resource"``.

By setting ``Fake.resource_key`` on *line 7*, we tell the ``Resource.create``,
``Resource.fetch``, and ``Resource.commit`` methods that we're either sending
or receiving a resource that is in a dictionary with that key.

By setting ``Fake.resources_key`` on *line 8*, we tell the ``Resource.list``
method that we're expecting to receive multiple resources inside a dictionary
with that key.

``base_path``
*************

The ``base_path`` is the URL we're going to use to make requests for this
resource. In this case, *line 9* sets ``base_path = "/fake"``, which also
corresponds to the name of our class, ``Fake``.

Most resources follow this basic formula. Some cases are more complex, where
the URL to make requests to has to contain some extra data. The volume service
has several resources which make either basic requests or detailed requests,
so they use ``base_path = "/volumes/%s(detailed)"``. Before a request is made,
if ``detailed = True``, they convert it to a string so the URL becomes
``/volumes/detailed``. If it's ``False``, they only send ``/volumes/``.

The Service
***********

Unlike ``resource_key``, ``resources_key`` and ``base_path``, the service a
resource belongs to is not declared on the resource itself. Instead, each
service provides a
:class:`~openstack.service_description.ServiceDescription` subclass -
``FakeService`` in ``fake_service.py`` - which maps each supported API version
to the proxy that exposes the service's resources.

In ``fake_service.py`` we set ``supported_versions`` so that version ``2`` of
the service is served by ``openstack.fake.v2._proxy.Proxy``. The proxy ties the
resources together and knows how to reach the service in the catalog, so that
when a request is made the appropriate URL can be constructed.

Supported Operations
--------------------

The base :class:`~openstack.resource.Resource` disallows all types of requests
by default, requiring each resource to specify which requests they support.
On *lines 11-16*, our ``Fake`` resource specifies that it'll work with all
of the operations.

In order to have the following methods work, you must allow the corresponding
value by setting it to ``True``:

+----------------------------------------------+----------------+
| :class:`~openstack.resource.Resource.create` | allow_create   |
+----------------------------------------------+----------------+
| :class:`~openstack.resource.Resource.delete` | allow_delete   |
+----------------------------------------------+----------------+
| :class:`~openstack.resource.Resource.head`   | allow_head     |
+----------------------------------------------+----------------+
| :class:`~openstack.resource.Resource.list`   | allow_list     |
+----------------------------------------------+----------------+
| :class:`~openstack.resource.Resource.fetch`  | allow_fetch    |
+----------------------------------------------+----------------+
| :class:`~openstack.resource.Resource.commit` | allow_commit   |
+----------------------------------------------+----------------+

An additional attribute to set is ``commit_method``. It defaults to ``PUT``,
but some services use ``POST`` or ``PATCH`` to commit changes back to the
remote resource.

Properties
----------

The way resource classes communicate values between the user and the server is
through a set of component objects. Each is declared as a class attribute and
maps an attribute on your :class:`~openstack.resource.Resource` to a value that
lives in a particular part of the request or response:

* ``resource.Body`` - a value carried in the JSON request or response body.
* ``resource.Header`` - a value carried in an HTTP header.
* ``resource.URI`` - a value that is interpolated into the ``base_path``.
* ``resource.Computed`` - a value that is computed locally rather than sent to
  or received from the server.

The first argument to each component is the name the value has on the server;
the attribute name is how you refer to it in Python.

*Line 19* declares a ``Header`` for ``timestamp``, which will cause the
``Fake.timestamp`` attribute to contain the value returned in the
``x-timestamp`` header, such as from a ``Fake.head`` request.

*Line 21* declares a ``Body`` for ``name``, which is a value returned in a
body, such as from a ``Fake.fetch`` request. Passing ``alternate_id=True``
marks this attribute as the resource's identifier, so when this resource is
populated from a response, ``Fake.name`` and ``Fake.id`` are the same value.

*Line 23* declares a ``Body`` with an ``alias``. ``Fake.value`` will be set
when a response body contains a ``value``, or when a header contains
``x-resource-value``.

*Line 26* passes ``type=bool``, which is checked before sending the value in a
request. In this case, we can only set ``Fake.cool`` to either ``True`` or
``False``, otherwise a ``TypeError`` will be raised if the value can't be
converted to the expected type.

Documentation
-------------

We use Sphinx's ``autodoc`` feature in order to build API documentation for
each resource we expose. The attributes we override from
:class:`~openstack.resource.Resource` don't need to be documented, but any
component attributes (``Body``, ``Header``, and so on) must be. All you need to
do is add a comment *above* the line to document, with a colon following the
pound-sign.

*Lines 18, 20, 22, and 24-25* are comments which will then appear in the API
documentation. As shown in *lines 24 & 25*, these comments can span multiple
lines.
