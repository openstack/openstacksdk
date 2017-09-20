import shade
shade.simple_logging()

cloud = shade.openstack_cloud(cloud='fuga', region_name='cystack')
cloud.pprint([
    image for image in cloud.list_images()
    if 'ubuntu' in image.name.lower()])
