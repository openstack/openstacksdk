Tasks Needed for rationalizing shade and openstacksdk
=====================================================

A large portion of the important things have already been done and landed
already. For reference, those are:

* shade and os-client-config library content have been merged into the tree.
* Use official service-type names from Service Types Authority via
  os-service-types to refer to services and proxies.
* Automatically also add properties to the connection for every known alias
  for each service-type.
* Made openstack.proxy.Proxy a subclass of keystoneauth1.adapter.Adapter.
  Removed local logic that duplicates keystoneauth logic. This means every
  proxy also has direct REST primitives available. For example:

  .. code-block:: python

    connection = connection.Connection()
    servers = connection.compute.servers()
    server_response = connection.compute.get('/servers')

* Removed the Profile object in favor of openstack.config.
* Removed the Session object in favor of using keystoneauth.
* Plumbed Proxy use of Adapter through the Adapter subclass from shade that
  uses the TaskManager to run REST calls.
* Finish migrating to Resource2 and Proxy2, rename them to Resource and Proxy.
* Merge OpenStackCloud into Connection. This should result
  in being able to use the connection interact with the cloud using all three
  interfaces. For instance:

  .. code-block:: python

    conn = connection.Connection()
    servers = conn.list_servers()  # High-level resource interface from shade
    servers = conn.compute.servers()  # SDK Service/Object Interface
    response = conn.compute.get('/servers')  # REST passthrough
* Removed ServiceFilter and the various Service objects in favor of discovery.

Next steps
==========

* Maybe rename self.session and session parameter in all usage in proxy and
  resource to self.adapter. They are Adapters not Sessions, but that may not
  mean anything to people.
* Migrate unit tests to requests-mock instead of mocking python calls to
  session.
* Replace _prepare_request with requests.Session.prepare_request.

shade integration
-----------------

* Invent some terminology that is clear and makes sense to distinguish between
  the object interface that came originally from openstacksdk and the
  interface that came from shade.
* Shift the shade interface methods to use the Object Interface for their
  operations. It's possible there may be cases where the REST layer needs to
  be used instead, but we should try to sort those out.
* Investigate options and then make a plan as to whether shade methods should
  return SDK objects or return dicts/munches as they do today. Should we make
  Resource objects extend dict/munch so they can be used like the shade ones
  today? Or should we just have the external shade shim library get objects
  from the high-level SDK 'shade' interface and call to_dict() on them all?
* Add support for shade expressing normalization model/contract into Resource,
  or for just leveraging what's in Resource for shade-layer normalization.
* Make a plan for normalization supporting shade users continuing
  to get shade normalized resource Munch objects from shade API calls, sdk
  proxy/resource users getting SDK objects, and both of them being able to opt
  in to "strict" normalization at Connection constructor time. Perhaps making
  Resource subclass Munch would allow mixed use? Needs investigation.
* Investigate auto-generating the bulk of shade's API based on introspection of
  SDK objects, leaving only the code with extra special logic in the shade
  layer.

Service Proxies
---------------

These are all things to think about.

* Authenticate at Connection() creation time? Having done that, use the
  catalog in the token to determine which service proxies to add to the
  Connection object.
* Filter the above service list from the token by has_service() from
  openstack.config.
* Add a has_service method to Connection which will BASICALLY just be
  hasattr(self, 'service') - but will look nicer.
* Consider adding magic to Connection for every service that a given cloud
  DOESN'T have that will throw an exception on any attribute access that is
  "cloud doesn't have service blah" rather than simply Attribute Not Found.
  The SDK has a python api regardless of the services remotely, it would be
  nice if trimming the existing attribute list wouldn't make it impossible for
  someone to validate their code correctness. It's also possible that instead
  of not having services, we always mount proxy objects for every service, but
  we mount a "NotFound" proxy for each service that isn't there.
* Since openstacksdk uses version discovery now, there is always a good path
  to "the" version of a given service. However, a cloud may have more than one.
  Attach the discovered service proxy to connection as today under the service
  type name. Add a property to each service proxy for each version the SDK
  knows about. For instance:

  .. code-block:: python

    connection = openstack.Connection()
    connection.volume     # openstack.volume.v3._proxy
    connection.volume.v2  # openstack.volume.v2._proxy
    connection.volume.v3  # openstack.volume.v3._proxy

  Those versioned proxies should be done as Adapters with min and max version
  set explicitly. This should allow a common pattern for people to write code
  that just wants to use the discovered or configured service, or who want to
  attempt to use a specific version of the API if they know what they're doing
  and at the very least wind up with a properly configured Adapter they can
  make rest calls on. Because:

  .. code-block:: python

    connection = openstack.Connection()
    connection.dns.v2.get('/zones')

  should always work on an OpenStack cloud with designate even if the SDK
  authors don't know anything about Designate and haven't added Resource or
  Proxy explicitly for it.
* Decide what todo about non-OpenStack services. Do we add base Proxy
  properties to Connection for every service we find in the catalog regardless
  of official/non-official? If so, do we let someone pass a dict of
  service-type, Proxy to connection that would let the provide a local service
  we don't know about? If we do that- we should disallow passing in overrides
  for services we DO know about to discourage people writing local tools that
  have different Compute behavior, for instance.

Microversions
-------------

* keystoneauth.adapter.Adapter knows how to send microversion headers, and
  get_endpoint_data knows how to fetch supported ranges. As microversion
  support is added to calls, it needs to be on a per-request basis. This
  has implications to both Resource and Proxy, as cloud payloads for data
  mapping can be different on a per-microversion basis.
