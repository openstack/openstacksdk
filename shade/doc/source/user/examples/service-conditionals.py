import openstack.cloud
openstack.cloud.simple_logging(debug=True)

cloud = openstack.cloud.openstack_cloud(cloud='kiss', region_name='region1')
print(cloud.has_service('network'))
print(cloud.has_service('container-orchestration'))
