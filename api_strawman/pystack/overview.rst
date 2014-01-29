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

--------------------
Clients
--------------------

In order to work with a service, you need to get a reference to the **client**
object for that service. The client is specific to the authenticated user and
the chosen region. You use standard dot notation to access the desired client.

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

    >> print context.East
    {'compute': <pystack.identity.Endpoint at 0x106142dd0>,
     'ec2': <pystack.identity.Endpoint at 0x1062c6490>,
     'identity': <pystack.identity.Endpoint at 0x1062c6510>,
     'image': <pystack.identity.Endpoint at 0x1061428d0>,
     's3': <pystack.identity.Endpoint at 0x106142e10>,
     'volume': <pystack.identity.Endpoint at 0x1062c6210>}

    >> print context.compute
    {u'RegionOne': <pystack.identity.Endpoint at 0x106142dd0>}

As you can see, referencing ``context.<region>`` returns a dictionary of
Endpoint objects, with the available services as the keys, and referencing
``context.<service>`` returns a dictionary keyed by region.

----------------------
Working with Clients
----------------------
Once you have a client, you can call its methods to interact with the service.
Clients have several standard methods that correspond to the basic REST
methods:

* ``list()``: Lists the available resources. This supports basic paging arguments.
* ``create(*args, **kwargs)``: Creates a new resource. The particular arguments required depend on the service.
* ``update(obj, **kwargs)``: Updates an existing resource with the supplied values.
* ``delete(obj)``: Deletes an existing resource.

