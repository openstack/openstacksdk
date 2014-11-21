============
Contributing
============

python-openstacksdk is a Stackforge project, mirrored on `GitHub`_.  Bugs and
Blueprints are handled on `Launchpad`_.  Code reviews are hosted on `Gerrit`_.

.. _GitHub: https://github.com/stackforge/python-openstacksdk
.. _Launchpad: https://launchpad.net/python-openstacksdk
.. _Gerrit: https://review.openstack.org/#/q/project:stackforge/python-openstacksdk,n,z

Getting Setup
-------------

Python
******

The python-openstacksdk project supports Python versions 2.6, 2.7, 3.3+, and
pypy, so you'll need to have at least one of those to get started.

virtualenv
**********

Rather than installing the project's dependencies into your system-wide Python
installation, you should create a virtual environment for this project.

Install
^^^^^^^

Debian based platforms::

   apt-get install -y python-virtualenv

RedHat based platforms::

   yum install -y python-virtualenv

Other::

   pip install virtualenv

Setup
^^^^^
::

   $ virtualenv sdk
   New python executable in sdk/bin/python
   Installing setuptools, pip...done.
   $ source sdk/bin/activate
   (sdk)$

Getting the code
****************

If you haven't contributed in the openstack community before, be sure to read:

  https://wiki.openstack.org/wiki/How_To_Contribute
  https://wiki.openstack.org/wiki/Gerrit_Workflow

and then you'll be ready to::

  git clone https://github.com/stackforge/python-openstacksdk.git

tox
***

We use `tox <https://tox.readthedocs.org>`_ as our test runner, as it provides
the ability to run your test against multiple versions. Going back to the
`Python`_ section, ideally you have all of the versions installed so tox
will accurately reflect how your code will run through the
`continuous integration <http://ci.openstack.org/>`_ system.::

   (sdk)$ pip install tox

To run tox, just execute the ``tox`` command. With no arguments, it runs
everything in our ``tox.ini`` file. You can also give it a specific
environment to run.::

   (sdk)$ tox
   (sdk)$ tox -e py33

Using the code
**************

To run the examples or otherwise use the SDK within your environment, you'll
need to get the project's dependencies.::

   (sdk)$ python setup.py develop
   ...
   (sdk)$ python
   >>> import openstack


Project Layout
--------------

The code is laid out in the following structure. This example shows files
relevant to working with code for the compute service's servers.::

   openstack/
       connection.py
       resource.py
       session.py
       transport.py
       auth/
           identity/
               v2.py
               v3.py
       compute/
           compute_service.py
           v2/
               server.py
               _proxy.py
       tests/
           compute/
               v2/
                   test_server.py

Session
*******

The :class:`openstack.session.Session` manages an authenticator,
transport, and user preferences. It exposes methods corresponding to
HTTP verbs, and injects your authentication token into a request,
determines any service preferences callers may have set, gets the endpoint
from the authenticator, and sends the request out through the transport.

Authenticator
^^^^^^^^^^^^^

As the `Session`_ needs a way to get a token and endpoint, it is constructed
with either a ``v2.Auth`` or ``v3.Auth`` object from
:mod:`openstack.auth.identity`. These two classes speak to OpenStack's Identity
service and are able to handle things like authentication tokens and their
expiration, and the service catalog.

Transport
^^^^^^^^^

The :class:`openstack.transport.Transport` class in is built on
`requests.Session <http://docs.python-requests.org/en/latest/user/advanced/>`_
and handles the sending of requests and receiving of responses.
``Transport.request`` handles the insertion of header values,
logging of the request and response and converts responses to JSON when
necessary.

The ``Transport._send_request`` method handles redirection status
codes returned from ``requests.Session.request``, as the requests library
follows a
`browser redirection pattern <https://en.wikipedia.org/wiki/Post/Redirect/Get>`_
that isn't suitable for this library.

Resource
********

The :class:`openstack.resource.Resource` base class is the building block
of any service implementation. ``Resource`` objects correspond to the
resources each service's REST API works with, so the
:class:`openstack.compute.v2.server.Server` subclass maps to the compute
service's ``https://openstack:1234/v2/servers`` resource.

The base ``Resource`` contains methods to support the typical
`CRUD <http://en.wikipedia.org/wiki/Create,_read,_update_and_delete>`_
operations supported by REST APIs, and handles the construction of URLs
and calling the appropriate HTTP verb on the given ``Session``.

Values sent to or returned from the service are implemented as attributes
on the ``Resource`` subclass with type :class:`openstack.resource.prop`.
The ``prop`` is created with the exact name of what the API expects,
and can optionally include a ``type`` to be validated against on requests.
You should choose an attribute name that follows PEP-8, regardless of what
the server-side expects, as this ``prop`` becomes a mapping between the two.::

   is_public = resource.prop('os-flavor-access:is_public', type=bool)

There are six additional attributes which the ``Resource`` class checks
before making requests to the REST API. ``allow_create``, ``allow_retreive``,
``allow_update``, ``allow_delete``, ``allow_head``, and ``allow_list`` are set
to ``True`` or ``False``, and are checked before making the corresponding
method call.

The ``base_path`` attribute should be set to the URL which corresponds to
this resource. Many ``base_path``\s are simple, such as ``"/servers"``.
For ``base_path``\s which are composed of non-static information, Python's
string replacement is used, e.g., ``base_path = "/servers/%(server_id)s/ips"``.

``resource_key`` and ``resources_key`` are attributes to set when a
``Resource`` returns more than one item in a response, or otherwise
requires a key to obtain the response value. For example, the ``Server``
class sets ``resource_key = "server"`` and ``resource_keys = "servers"``
to support the fact that multiple ``Server``\s can be returned, and each
is identified with a singular noun in the response.

Proxy
*****

Each service implements a ``Proxy`` class, within the
``openstack/<program_name>/vX/_proxy.py`` module. For example, the v2 compute
service's ``Proxy`` exists in ``openstack/compute/v2/_proxy.py``.

Each ``Proxy`` class implements methods which act on the underlying
``Resource`` classes which represent the service. For example::

   def list_flavors(self, **params):
       return flavor.Flavor.list(self.session, **params)

This method is operating on the ``openstack.compute.v2.flavor.Flavor.list``
method. For the time being, it simply passes on the ``Session`` maintained
by the ``Proxy``, and returns what the underlying ``Resource.list`` method
does.

The implementations and method signatures of ``Proxy`` methods are currently
under construction, as we figure out the best way to implement them in a
way which will apply nicely across all of the services.

Connection
**********

The :class:`openstack.connection.Connection` class builds atop a ``Session``
object, and provides a higher level interface constructed of ``Proxy``
objects from each of the services.

The ``Connection`` class' primary purpose is to act as a high-level interface
to this SDK, managing the lower level connecton bits and exposing the
``Resource`` objects through their corresponding `Proxy`_ object.

If you've built proper ``Resource`` objects and implemented methods on the
corresponding ``Proxy`` object, the high-level interface to your service
should now be exposed.

Contacting the Team
-------------------

IRC
***

The developers of this project are available in the
`#openstack-sdks <http://webchat.freenode.net?channels=%23openstack-sdks>`_
channel on Freenode.

Email
*****

The `openstack-dev <mailto:openstack-dev@openstack.org?subject=[python-openstacksdk]%20Question%20about%20the%20python-openstacksdk>`_
mailing list fields questions of all types on OpenStack. Using the
``[python-openstacksdk]`` filter to begin your email subject will ensure
that the message gets to SDK developers.

If you're interested in communicating one-on-one, the following developers
of the project are available:

* Brian Curtin <brian@python.org>
