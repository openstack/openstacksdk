import shade

# Initialize and turn on debug logging
shade.simple_logging(debug=True)

for cloud_name, region_name, image, flavor in [
        ('my-vexxhost', 'ca-ymq-1',
         'Ubuntu 16.04.1 LTS [2017-03-03]', 'v1-standard-4'),
        ('my-citycloud', 'Buf1',
         'Ubuntu 16.04 Xenial Xerus', '4C-4GB-100GB'),
        ('my-internap', 'ams01',
         'Ubuntu 16.04 LTS (Xenial Xerus)', 'A1.4')]:
    # Initialize cloud
    cloud = shade.openstack_cloud(cloud=cloud_name, region_name=region_name)
    cloud.delete_server('my-server', wait=True, delete_ips=True)

    # Boot a server, wait for it to boot, and then do whatever is needed
    # to get a public ip for it.
    server = cloud.create_server(
        'my-server', image=image, flavor=flavor, wait=True, auto_ip=True)
    print(server.name)
    print(server['name'])
    cloud.pprint(server)
    # Delete it - this is a demo
    cloud.delete_server(server, wait=True, delete_ips=True)
