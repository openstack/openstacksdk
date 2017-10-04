import openstack.cloud
openstack.cloud.simple_logging(debug=True)

cloud = openstack.openstack_cloud(
    cloud='my-vexxhost', region_name='ca-ymq-1')
cloud.get_image('Ubuntu 16.04.1 LTS [2017-03-03]')
