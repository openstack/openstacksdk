import shade

# Initialize and turn on debug logging
shade.simple_logging(debug=True)

for cloud_name, region_name, image, flavor_id in [
        ('my-vexxhost', 'ca-ymq-1', 'Ubuntu 16.04.1 LTS [2017-03-03]',
         '5cf64088-893b-46b5-9bb1-ee020277635d'),
        ('my-citycloud', 'Buf1', 'Ubuntu 16.04 Xenial Xerus',
         '0dab10b5-42a2-438e-be7b-505741a7ffcc'),
        ('my-internap', 'ams01', 'Ubuntu 16.04 LTS (Xenial Xerus)',
         'A1.4')]:
    # Initialize cloud
    cloud = shade.openstack_cloud(cloud=cloud_name, region_name=region_name)

    # Boot a server, wait for it to boot, and then do whatever is needed
    # to get a public ip for it.
    server = cloud.create_server(
        'my-server', image=image, flavor=dict(id=flavor_id),
        wait=True, auto_ip=True)
    # Delete it - this is a demo
    cloud.delete_server(server, wait=True, delete_ips=True)
