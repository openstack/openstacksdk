Session
=======

.. automodule:: openstack.session

Session Object
--------------

.. autoclass:: openstack.session.Session
   :members:

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
