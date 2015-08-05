************************
Future Design Discussion
************************

This document discusses a new approach to the Shade library and how
we might wish for it to operate in a future, not-yet-developed version.
It presents a more object oriented approach, and design decisions that
we have learned and decided on while working on the current version.

Object Design
=============

Shade is a library for managing resources, not for operating APIs. As such,
it is the resource in question that is the primary object and not the service
that may or may not provide that resource, much as we may feel warm and fuzzy
to one of the services.

Every resource at minimum has CRUD functions. Additionally, every resource
action should have a "do this task blocking" or "request that the cloud start
this action and give me a way to check its status" The creation and deletion
of Resources will be handled by a ResourceManager that is attached to the Cloud
::

    class Cloud:
      ResourceManager<Server> server
      servers = server
      ResourceManager<FloatingIp> floating_ip
      floating_ips = floating_ip
      ResourceManager<Image> image
      images = image
      ResourceManager<Role> role
      roles = role
      ResourceManager<Volume> volume
      volumes = volume

getting, listing and searching
------------------------------

In addition to creating a resource, there are different ways of getting your
hands on a resource. A `get`, a `list` and a `search`.

`list` has the simplest semantics - it takes no parameters and simply returns
a list of all of the resources that exist.

`search` takes a set of parameters to match against and returns a list of
resources that match the parameters given. If no resources match, it returns
an empty list.

`get` takes the same set of parameters that `search` takes, but will only ever
return a single matching resource or None. If multiple resources are matched,
an exception will be raised.

::

    class ResourceManager<Resource>:
      def get -> Resource
      def list -> List<Resource>
      def search -> List<Resource>
      def create -> Resource

Cloud and ResourceManager interface
===================================

All ResourceManagers should accept a cache object passed in to their constructor
and should additionally pass that cache object to all Resource constructors.
The top-level cloud should create the cache object, then pass it to each of
the ResourceManagers when it creates them.

Client connection objects should exist and be managed at the Cloud level. A
backreference to the OpenStack cloud should be passed to every resource manager
so that ResourceManagers can get hold of the ones they need. For instance,
an Image ResourceManager would potentially need access to both the glance_client
and the swift_client.

::

    class ResourceManager
      def __init__(self, cache, cloud)
    class ServerManager(ResourceManager)
    class OpenStackCloud
      def __init__(self):
        self.cache = dogpile.cache()
        self.server = ServerManager(self.cache, self)
        self.servers = self.server

Any resources that have an association action - such as servers and
floating_ips, should carry reciprocal methods on each resource with absolutely
no difference in behavior.

::

    class Server(Resource):
      def connect_floating_ip:
    class FloatingIp(Resource):
      def connect_server:

Resource objects should have all of the accessor methods you'd expect, as well
as any other interesting rollup methods or actions. For instance, since
a keystone User can be enabled or disabled, one should expect that there
would be an enable() and a disable() method, and that those methods will
immediately operate the necessary REST apis. However, if you need to make 80
changes to a Resource, 80 REST calls may or may not be silly, so there should
also be a generic update() method which can be used to request the minimal
amount of REST calls needed to update the attributes to the requested values.

Resource objects should all have a to_dict method which will return a plain
flat dictionary of their attributes.

::

    class Resource:
      def update(**new_values) -> Resource
      def delete -> None, throws on error

Readiness
---------

`create`, `get`, and `attach` can return resources that are not yet ready. Each
method should take a `wait` and a `timeout` parameter, that will cause the
request for the resource to block until it is ready. However, the user may
want to poll themselves. Each resource should have an `is_ready` method which
will return True when the resource is ready. The `wait` method then can
actually be implemented in the base Resource class as an iterate timeout
loop around calls to `is_ready`. Every Resource should also have an
`is_failed` and an `is_deleted` method.

Optional Behavior
-----------------

Not all clouds expose all features. For instance, some clouds do not have
floating ips. Additionally, some clouds may have the feature but the user
account does not, which is effectively the same thing.
This should be handled in several ways:

If the user explicitly requests a resource that they do not have access to,
an error should be raised. For instance, if a user tries to create a floating
ip on a cloud that does not expose that feature to them, shade should throw
a "Your cloud does not let you do that" error.

If the resource concept can be can be serviced by multiple possible services,
shade should transparently try all of them. The discovery method should use
the dogpile.cache mechanism so that it can be avoided on subsequent tries. For
instance, if the user says "please upload this  image", shade should figure
out which sequence of actions need to be performed and should get the job done.

If the resource isn't present on some clouds, but the overall concept the
resource represents is, a different resource should present the concept. For
instance, while some clouds do not have floating ips, if what the user wants
is "a server with an IP" - then the fact that one needs to request a floating
ip on some clouds is a detail, and the right thing for that to be is a quality
of a server and managed by the server resource. A floating ip resource should
really only be directly manipulated by the user if they were doing something
very floating-ip specific, such as moving a floating ip from one server to
another.

In short, it should be considered a MASSIVE bug in shade if the shade user
ever has to have in their own code "if cloud.has_capability("X") do_thing
else do_other_thing" - since that construct conveys some resource that shade
should really be able to model.

Functional Interface
====================

shade should also provide a functional mapping to the object interface that
does not expose the object interface at all. For instance, for a resource type
`server`, one could expect the following.

::

  class OpenStackCloud:
    def create_server
        return self.server.create().to_dict()
    def get_server
        return self.server.get().to_dict()
    def update_server
        return self.server.get().update().to_dict()
