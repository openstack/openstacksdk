import openstack.cloud
openstack.cloud.simple_logging(debug=True)

cloud = openstack.cloud.openstack_cloud(cloud='rax', region_name='DFW')
print(cloud.has_service('network'))
