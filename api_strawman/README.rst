An OpenStack all-in-one SDK
===========================

Notes and mockups for a unified OpenStack SDK.

Example:

.. code-block:: python

    import io

    from openstack import OpenStackClient, KeystoneAuth


    client = OpenStackClient(KeystoneAuth('http://localhost:8000/', 'alex', '****'))
    image = client.compute.images.list()[0]
    server = client.compute.servers.create(image=image)
    print server.public_ips[0]

    container = client.object_storage.containers.create(name='stuff')
    container.objects.create(name='a thing', contents=io.BytesIO(b'all the bytes'))

.. code-block:: python

    import pystack
    from pystack.identity import KeystoneIdentity
    ident = KeystoneIdentity(username="ed", tenant_id="1234567890abcdef",
            password="******", auth_endpoint="http://123.123.123.123:5000/v2.0/")
    context = ident.authenticate()
    services_for_region = context.some_region
    compute_client = services_for_region.compute.client
    image = compute_client.list_images()[0]
    server = compute_client.create("server_name", image=image)

    storage_client = services_for_region.object_storage.client
    container = storage_client.create("stuff")
    obj = container.create(file_or_path="/path/to/my/cool.jpg")
