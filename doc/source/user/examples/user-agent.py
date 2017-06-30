import shade
shade.simple_logging(http_debug=True)

cloud = shade.openstack_cloud(
    cloud='datacentred', app_name='AmazingApp', app_version='1.0')
cloud.list_networks()
