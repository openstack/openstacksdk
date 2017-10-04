import openstack.cloud
openstack.cloud.simple_logging()

cloud = openstack.openstack_cloud(cloud='fuga', region_name='cystack')
image = cloud.get_image(
    'Ubuntu 16.04 LTS - Xenial Xerus - 64-bit - Fuga Cloud Based Image')
cloud.pprint(image)
