# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import os_client_config
import time
import unittest

from keystoneauth1 import exceptions as _exceptions
from openstack import connection

#: Defines the OpenStack Client Config (OCC) cloud key in your OCC config
#: file, typically in $HOME/.config/openstack/clouds.yaml. That configuration
#: will determine where the functional tests will be run and what resource
#: defaults will be used to run the functional tests.
TEST_CLOUD = os.getenv('OS_CLOUD', 'devstack-admin')


class Opts(object):
    def __init__(self, cloud_name='devstack-admin', debug=False):
        self.cloud = cloud_name
        self.debug = debug


def _get_resource_value(resource_key, default):
    try:
        return cloud.config['functional'][resource_key]
    except KeyError:
        return default


opts = Opts(cloud_name=TEST_CLOUD)
occ = os_client_config.OpenStackConfig()
cloud = occ.get_one_cloud(opts.cloud, argparse=opts)

IMAGE_NAME = _get_resource_value('image_name',
                                 'Community_Ubuntu_16.04_TSI_latest')
FLAVOR_NAME = _get_resource_value('flavor_name', 's1.medium')


def service_exists(**kwargs):
    """Decorator function to check whether a service exists

    Usage:
    @unittest.skipUnless(base.service_exists(service_type="metering"),
                         "Metering service does not exist")
    class TestMeter(base.BaseFunctionalTest):
        ...

    :param kwargs: The kwargs needed to filter an endpoint.
    :returns: True if the service exists, otherwise False.
    """
    try:
        conn = connection.from_config(cloud_name=TEST_CLOUD)
        conn.session.get_endpoint(**kwargs)

        return True
    except _exceptions.EndpointNotFound:
        return False


class BaseFunctionalTest(unittest.TestCase):
    router = None
    subnet = None
    keypair = None

    @classmethod
    def setUpClass(cls):
        os.environ.setdefault(
            'OS_CLOUD_EYE_ENDPOINT_OVERRIDE',
            'https://ces.eu-de.otc.t-systems.com/V1.0/%(project_id)s'
        )
        os.environ.setdefault(
            'OS_AUTO_SCALING_ENDPOINT_OVERRIDE',
            ('https://as.eu-de.otc.t-systems.com'
             '/autoscaling-api/v1/%(project_id)s')
        )
        os.environ.setdefault(
            'OS_VOLUME_BACKUP_ENDPOINT_OVERRIDE',
            'https://vbs.eu-de.otc.t-systems.com/v2/%(project_id)s'
        )
        os.environ.setdefault(
            'OS_LOAD_BALANCER_ENDPOINT_OVERRIDE',
            'https://elb.eu-de.otc.t-systems.com/v1.0/%(project_id)s'
        )
        os.environ.setdefault(
            'OS_MAP_REDUCE_ENDPOINT_OVERRIDE',
            'https://mrs.eu-de.otc.t-systems.com/v1.1/%(project_id)s'
        )
        cls.conn = connection.from_config(cloud_name=TEST_CLOUD)

    @classmethod
    def assertIs(cls, expected, actual):
        if expected != actual:
            raise Exception(expected + ' != ' + actual)

    @classmethod
    def linger_for_delete(cls):
        time.sleep(40)

    @classmethod
    def get_first_router(cls):
        if cls.router:
            return cls.router
        else:
            routers = cls.conn.network.routers(limit=1)
            for _router in routers:
                cls.router = _router
                return cls.router

        raise Exception("No router available for testing")

    @classmethod
    def get_first_subnet(cls, router=None):
        if cls.subnet:
            return cls.subnet
        else:
            router = router if router else cls.get_first_router()
            subnets = cls.conn.network.subnets(limit=1, router_id=router.id)
            for _subnet in subnets:
                cls.subnet = _subnet
                return cls.subnet

        raise Exception("No subnet available for testing")

    @classmethod
    def get_first_keypair(cls):
        if cls.keypair:
            return cls.keypair
        else:
            keypairs = cls.conn.compute.keypairs()
            for _keypair in keypairs:
                cls.keypair = _keypair
                return cls.keypair

        raise Exception("No keypair available for testing")
