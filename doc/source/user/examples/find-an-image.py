import openstack.cloud
openstack.cloud.simple_logging()

cloud = openstack.openstack_cloud(cloud='fuga', region_name='cystack')
cloud.pprint([
    image for image in cloud.list_images()
    if 'ubuntu' in image.name.lower()])
