import openstack.cloud
openstack.cloud.simple_logging(http_debug=True)

cloud = openstack.openstack_cloud(
    cloud='datacentred', app_name='AmazingApp', app_version='1.0')
cloud.list_networks()
