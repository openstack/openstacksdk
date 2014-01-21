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
