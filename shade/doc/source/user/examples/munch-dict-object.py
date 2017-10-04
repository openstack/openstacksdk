import openstack.cloud
openstack.cloud.simple_logging(debug=True)

cloud = openstack.cloud.openstack_cloud(cloud='ovh', region_name='SBG1')
image = cloud.get_image('Ubuntu 16.10')
print(image.name)
print(image['name'])
