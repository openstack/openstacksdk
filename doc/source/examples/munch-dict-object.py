import shade
shade.simple_logging(debug=True)

cloud = shade.openstack_cloud(cloud='ovh', region_name='SBG1')
image = cloud.get_image('Ubuntu 16.10')
print(image.name)
print(image['name'])
