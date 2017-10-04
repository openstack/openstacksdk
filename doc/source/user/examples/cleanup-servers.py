import openstack.cloud

# Initialize and turn on debug logging
openstack.cloud.simple_logging(debug=True)

for cloud_name, region_name in [
        ('my-vexxhost', 'ca-ymq-1'),
        ('my-citycloud', 'Buf1'),
        ('my-internap', 'ams01')]:
    # Initialize cloud
    cloud = openstack.openstack_cloud(cloud=cloud_name, region_name=region_name)
    for server in cloud.search_servers('my-server'):
        cloud.delete_server(server, wait=True, delete_ips=True)
