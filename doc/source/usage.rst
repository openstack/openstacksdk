=====
Usage
=====

To use shade in a project::

	import shade

.. note::
  API methods that return a description of an OpenStack resource (e.g.,
  server instance, image, volume, etc.) do so using a dictionary of values
  (e.g., ``server['id']``, ``image['name']``). This is the standard, and
  **recommended**, way to access these resource values.

  For backward compatibility, resource values can be accessed using object
  attribute access (e.g., ``server.id``, ``image.name``). Shade uses the
  `Munch library <https://github.com/Infinidat/munch>`_ to provide this
  behavior. This is **NOT** the recommended way to access resource values.
  We keep this behavior for developer convenience in the 1.x series of shade
  releases. This will likely not be the case in future, major releases of shade.

.. autoclass:: shade.OpenStackCloud
   :members:

.. autoclass:: shade.OperatorCloud
   :members:
