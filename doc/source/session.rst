Session
=======

``openstack.session.Session`` is the class that maintains session layer
similar to the OSI model session layer.  The session has a transport and
an authenticator.  The transport is used by the session and authenticator
for HTTP layer transport.  The authenticator is responsible for providing an
authentication token and an endpoint to communicate with.

Session object
--------------

.. class:: openstack.session.Session(transport, authenticator)

   Create a new ``Session`` object with a transport and authenticator.

   * transport -  Transport such as ``openstack.transport.Transport`` that
     provides an HTTP request method.  The transport is also to be used by
     the authenticator if needed.
   * authenticator - An authenticator derived from
     ``openstack.auth.base.BaseAuthPlugin`` that provides get_token and
     get_endpoint methods for the session.

   All the other methods of the session accept the following parameters:

   * service - a service filter for the authenticator to determine the
     correct endpoint to use.
   * authenticate - A flag that indicates if a token should be attached to the
     request.  This parameter defaults to true.
   * kwargs - The remaining arguments are passed to the transport request
     method.

   .. method:: head(url, service=service_filter, authenticate=True, **kwargs)

      Perform an HTTP HEAD request.

   .. method:: get(url, service=service_filter, authenticate=True, **kwargs)

      Perform an HTTP GET request.

   .. method:: post(url, service=service_filter, authenticate=True, **kwargs)

      Perform an HTTP POST request.

   .. method:: put(url, service=service_filter, authenticate=True, **kwargs)

      Perform an HTTP PUT request.

   .. method:: delete(url, service=service_filter, authenticate=True, **kwargs)

      Perform an HTTP DELTE request.

   .. method:: patch(url, service=service_filter, authenticate=True, **kwargs)

      Perform an HTTP PATCH request.

Examples
--------

The following examples use the example authenticator which takes the token
and endpoint as arguments.

Create a session
~~~~~~~~~~~~~~~~

Constructor::

    from examples import authenticator
    from openstack import session
    from openstack import transport
    xport = transport.Transport()
    token = 'SecretToken'
    endpoint = 'http://cloud.example.com:3333'
    auther = authenticator.TestAuthenticator(token, endpoint)
    sess = session.Session(xport, auther)

HTTP GET
~~~~~~~~

Making a basic HTTP GET call::

    containers = sess.get('/').json()

The containers variable will contain a list of dict describing the containers.

HTTP PUT
~~~~~~~~

Creating a new object::

    objay_data = 'roland garros'
    objay_len = len(objay_data)
    headers = {"Content-Length": objay_len, "Content-Type": "text/plain"}
    resp = sess.put('/pilots/french.txt', headers=headers, data=objay_data)
