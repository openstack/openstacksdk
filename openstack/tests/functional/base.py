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
import openstack.config

from keystoneauth1 import exceptions as _exceptions
from openstack import connection
from openstack.tests import base


#: Defines the OpenStack Client Config (OCC) cloud key in your OCC config
#: file, typically in $HOME/.config/openstack/clouds.yaml. That configuration
#: will determine where the functional tests will be run and what resource
#: defaults will be used to run the functional tests.
TEST_CLOUD_NAME = os.getenv('OS_CLOUD', 'devstack-admin')
TEST_CLOUD_REGION = openstack.config.get_cloud_region(cloud=TEST_CLOUD_NAME)


def _get_resource_value(resource_key, default):
    try:
        return TEST_CLOUD_REGION.config['functional'][resource_key]
    except KeyError:
        return default


IMAGE_NAME = _get_resource_value('image_name', 'cirros-0.3.5-x86_64-disk')
FLAVOR_NAME = _get_resource_value('flavor_name', 'm1.small')


class BaseFunctionalTest(base.TestCase):

    def setUp(self):
        super(BaseFunctionalTest, self).setUp()
        self.conn = connection.Connection(config=TEST_CLOUD_REGION)

    def addEmptyCleanup(self, func, *args, **kwargs):
        def cleanup():
            result = func(*args, **kwargs)
            self.assertIsNone(result)
        self.addCleanup(cleanup)

    # TODO(shade) Replace this with call to conn.has_service when we've merged
    #             the shade methods into Connection.
    def require_service(self, service_type, **kwargs):
        """Method to check whether a service exists

        Usage:
        class TestMeter(base.BaseFunctionalTest):
            ...
            def setUp(self):
                super(TestMeter, self).setUp()
                self.require_service('metering')

        :returns: True if the service exists, otherwise False.
        """
        try:
            self.conn.session.get_endpoint(service_type=service_type, **kwargs)
        except _exceptions.EndpointNotFound:
            self.skipTest('Service {service_type} not found in cloud'.format(
                service_type=service_type))
