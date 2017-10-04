import openstack.cloud
openstack.cloud.simple_logging(debug=True)

cloud = openstack.openstack_cloud(cloud='rax', region_name='DFW')
print(cloud.has_service('network'))
