=====
Usage
=====

To use shade in a project::

	import shade

.. warning::
  Several of the API methods return a ``dict`` that describe a resource.
  It is possible to access keys of the dict as an attribute (e.g.,
  ``server.id`` instead of ``server['id']``) to maintain some backward
  compatibility, but attribute access is deprecated. New code should
  assume a normal dictionary and access values via key.

.. automodule:: shade
   :members:
