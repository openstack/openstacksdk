import shade
shade.simple_logging(debug=True)

cloud = shade.openstack_cloud(cloud='rax', region_name='DFW')
print(cloud.has_service('network'))
