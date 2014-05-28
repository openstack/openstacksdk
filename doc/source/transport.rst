Transport
=========

Class ``openstack.transport.Transport`` is a subclass of ``requests.Session``
that adds some features that are common in OpenStack APIs or can be globally
controlled by an application.  Its use is incredibly similar to
``requests.Session`` such that we only will cover the differences in detail
here.

Transport object
----------------

.. class:: openstack.transport.Transport(user_agent=None, verify=True, redirect=DEFAULT_REDIRECT_LIMIT)

Create a new ``Transport`` object.  In addition to those listed below, all
arguments available to ``requests.Session`` are available here:

* user_agent -  Set the default ``User-Agent`` header (default: ``None``)
* verify - If ``True``, the SSL cert will be verified.  It can also be set to
  a CA_BUNDLE path.  (default: ``True``)
* redirect - Disallow redirects if ``False``, or allow ``requests.Session`` to
  handle redirects if ``True``. An integer can instead be passed to specify
  the maximum number of redirections followed.

Method ``Transport.request(method, url, redirect=None, **kwargs)``

Perform an HTTP request. The following arguments differ from
``requests.Session``:

* redirect - (integer) The maximum number of redirections followed in a
  request. (boolean) No redirections if False, ``requests.Session`` handles
  redirection if True. (default:
  ``openstack.transport.DEFAULT_REDIRECT_LIMIT``)
* json - Request body to be encoded as JSON.  Overwrites ``data`` argument if
  present. (default: ``None``)
* user_agent -  Set the default ``User-Agent`` header (default: ``None``)

Examples
--------

Basic HTTP GET
~~~~~~~~~~~~~~

Making a basic HTTP GET call is very simple::

    from openstack import transport
    trans = transport.Transport()
    versions = trans.get('cloud.example.com:5000').json()

will retrieve the version data served by the Identity API into a Python dict.

HTTP POST
~~~~~~~~~

Creating a new object in an OpenStack service is similarly simple::

    from openstack import transport
    trans = transport.Transport()
    new_record = {'name': 'The White Albumn', 'artist': 'The Beatles'}
    resp = trans.post('cloud.example.com:4999/record', json=new_record)

Passing in the new_record dict with the ``json`` keyword argument performs the
``json.dumps()`` prior to the request being sent.  This is an addition to
the capabilities of ``requests.Session``.

Additional HTTP Methods
~~~~~~~~~~~~~~~~~~~~~~~

Just as in ``requests.Session``, all of the HTTP verbs have corresponding
methods in the ``Transport`` object.

SSL/TLS and Certificates
~~~~~~~~~~~~~~~~~~~~~~~~

The ``verify`` argument to ``Transport.request()`` can now be set when the
Transport object is created.  It can still be overwritten during any
individual call to ``request()`` or the HTTP verb methods.

To set the default hostname verification for the Transport to use a custom
CA certificate file::

    from openstack import transport
    trans = transport.Transport(verify='/etc/tls/local-ca-certs.crt')

The same usage from ``requests`` is still available.  To use the default CA
certificate file for a single request::

    versions = trans.get('cloud.example.com:5000', verify=True)

Or hit on a host with a self-signed certificate::

    versions = trans.get('cloud.example.com:5000', verify=None)

Redirection
~~~~~~~~~~~

Redirection handling differs from ``requests`` by default as this module is
expected to be primarily used for querying REST API servers.  The redirection
model differs in that ``requests`` follows some browser patterns where it
will redirect POSTs as GETs for certain statuses which is not want we want
for an API.

See: https://en.wikipedia.org/wiki/Post/Redirect/Get

User Agent
~~~~~~~~~~

The ``User-Agent`` header may be set when the Transport object is created in
addition to the existing per-request mode.  The determination of how to set
the ``User-Agent`` header is as follows:

* If the ``user_agent`` argument is included in the ``request()`` call use it
* Else if ``User-Agent`` is set in the headers dict use it
* Else if ``user_agent`` argument is included in the ``Transport`` construction
  use it
* Else use ``transport.DEFAULT_USER_AGENT``
