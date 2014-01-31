============
Quick Start
============

Let's start by looking at some typical code; after that, we'll explain what
each part is doing and why it works that way. Here is how you authenticate and
get a list of your compute resources::

    import pystack
    context = pystack.identity.KeystoneIdentity("username", "password",
            "tenant_id")
    context.authenticate()

    clt = context.RegionOne.compute.client
    # Get a list of servers
    clt.list()
    # Get a list of all images
    clt.list_images()
    # Get a list of just saved snapshots
    clt.list_snapshots()

    # Get the object storage client
    clt_swift = context.RegionOne.object_store.client
    # List the containers
    containers = clt_swift.list()
    # Get the container named 'Photos'
    photo_cont = clt_swift.get("Photos")
    # Get the objects in that container
    photos = photo_cont.list()
    # Show the first photo
    print(photos[0])

    <StorageObject bytes=2445839, content_type=image/jpeg,
        hash=b61cbc2d01fcb897d37614d1db23d9fb,
        last_modified=2012-12-10T16:06:12.416920, name=family/IMG_0086.jpg>

====================
The Context Object
====================

In order to access your OpenStack resources, you need to authenticate. Once
authenticated, you have access to the services returned in the service catalog.
The context object handles the details of this for you. You may create multiple
context objects if you need to work with more than one user, tenant, or even
different OpenStack providers. The context object provides all of the client
objects you need to work with the various services available to you.

The primary class for context objects is **KeystoneIdentity**; if your provider
requires a different authentication mechanism, they will need to provide an
appropriate subclass to handle the differences. You can pass in your
credentials when you create the instance, pass them as arguments to the
`authenticate()` call, use the `keyring_auth()` method to use credentials
stored in your system's keychain, or use environment variables to hold that
information.

Once you have authenticated, the context object holds the information you need
to work with your OpenStack provider:

* **regions**: Returns a list of all available regions for your provider.
* **services**: Returns a dictionary whose keys are the service names, and whose values are Service objects.
* **service_catalog**: Holds the service catalog returned by the provider.

After authenticating, the primary use for a Context Object is to get the
appropriate Client object for the service and region you wish to work with.
Once you have the client objects you need, you will rarely need to interact
with the Context Object again. The only exceptions would be the admin identity
functions for managing users.

--------------------
Clients
--------------------

In order to work with a service, you need to get a reference to the **client**
object for that service. The client is specific to the authenticated user,
service, and the chosen region. You use standard dot notation to access the
desired client.

As an example, let's assume that your provider has four regions: North, East,
South, and West. To get the compute client for the East region, you can do
either of the following::

    clt = context.East.compute.client
    # -or-
    clt = context.compute.East.client

Why the duplication? Well, it's because sometimes you need to determine all the
services available in a given region, and at other times you may need to
determine all of the regions that a particular service is available in. Pystack
handles the resolution of both of these cases for you. For example::

    >> print(context.East)
    {'compute': <pystack.identity.Endpoint at 0x106142dd0>,
     'ec2': <pystack.identity.Endpoint at 0x1062c6490>,
     'identity': <pystack.identity.Endpoint at 0x1062c6510>,
     'image': <pystack.identity.Endpoint at 0x1061428d0>,
     's3': <pystack.identity.Endpoint at 0x106142e10>,
     'volume': <pystack.identity.Endpoint at 0x1062c6210>}

    >> print(context.compute)
    {u'RegionOne': <pystack.identity.Endpoint at 0x106142dd0>}

As you can see, referencing ``context.<region>`` returns a dictionary of
Endpoint objects, with the available services as the keys, and referencing
``context.<service>`` returns a dictionary keyed by region.

Some services expose private (internal) endpoints, i.e., for accessing the service using an internal private network, which would improve efficiency and reduce bandwidth usage. If such an endpoint exists, you can get the client for it by using the ``client_private`` attribute. For example::

    clt_priv = context.East.object_store.client_private

If there is no private endpoint defined for that service, a ``NoEndpointForService`` exception will be raised.

Clients also have a reference to the Context Object that created it, so that if
any request returns a 401 due to an expired token, the client will ask the
Context Object to re-authenticate to obtain a fresh token. If this succeeds,
the client will then re-issue the request. This all happens transparently to
the application built on pystack, allowing the developer to create long-running
applications without having to worry about token expiration.

----------------------
Working with Clients
----------------------
Once you have a client, you can call its methods to interact with the service.
Clients have several standard methods that correspond to the basic REST
methods:

* ``list()``: Lists the available resources. This supports basic paging arguments.
* ``create(*args, **kwargs)``: Creates a new resource. The particular arguments required depend on the servicei and the resource being created.
* ``update(obj, **kwargs)``: Updates an existing resource with the supplied values.
* ``delete(obj)``: Deletes an existing resource.

Additonally, clients have methods to handle all of the interaction you will
need with the API.

----------------------
Working with Resources
----------------------
Resource objects represent cloud resources: servers, images, stored objects,
networks, etc.

The attributes of a Resource represent the state of that resource in the cloud,
and depend on the type of resource. For example, when listing the stored
objects in a Swift container, the API returns a JSON dict like this::

    {"hash": "194577a7e20bdcc7afbb718f502c134c",
    "last_modified": "2012-12-10T16:06:12.115680",
    "bytes": 6148,
    "name": "some/object/name.txt",
    "content_type": "text/plain"}

The Resource object returned by pystack for this object would have the
attributes "hash", "last_modified", "bytes", "name", and "content_type", with
values corresponding to the values returned by the API.

Resource objects also have methods for operations that affect them. For
example, while you can always call the client to delete an object::

    clt.delete(obj)

... you can also call ``delete()`` directly on the resource itself::

    obj.delete()
