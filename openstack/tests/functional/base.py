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

from keystoneauth1 import discover
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


def _disable_keep_alive(conn):
    sess = conn.config.get_session()
    sess.keep_alive = False


IMAGE_NAME = _get_resource_value('image_name', 'cirros-0.4.0-x86_64-disk')
FLAVOR_NAME = _get_resource_value('flavor_name', 'm1.small')


class BaseFunctionalTest(base.TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseFunctionalTest, cls).setUpClass()
        # Defines default timeout for wait_for methods used
        # in the functional tests
        cls._wait_for_timeout = int(os.getenv(
            'OPENSTACKSDK_FUNC_TEST_TIMEOUT',
            300))

    def setUp(self):
        super(BaseFunctionalTest, self).setUp()
        self.conn = connection.Connection(config=TEST_CLOUD_REGION)
        _disable_keep_alive(self.conn)

        self._demo_name = os.environ.get('OPENSTACKSDK_DEMO_CLOUD', 'devstack')
        self._op_name = os.environ.get(
            'OPENSTACKSDK_OPERATOR_CLOUD', 'devstack-admin')

        self.config = openstack.config.OpenStackConfig()
        self._set_user_cloud()
        self._set_operator_cloud()

        self.identity_version = \
            self.operator_cloud.config.get_api_version('identity')

    def _set_user_cloud(self, **kwargs):
        user_config = self.config.get_one(
            cloud=self._demo_name, **kwargs)
        self.user_cloud = connection.Connection(config=user_config)
        _disable_keep_alive(self.user_cloud)

    def _set_operator_cloud(self, **kwargs):
        operator_config = self.config.get_one(
            cloud=self._op_name, **kwargs)
        self.operator_cloud = connection.Connection(config=operator_config)
        _disable_keep_alive(self.operator_cloud)

    def pick_image(self):
        images = self.user_cloud.list_images()
        self.add_info_on_exception('images', images)

        image_name = os.environ.get('OPENSTACKSDK_IMAGE')
        if image_name:
            for image in images:
                if image.name == image_name:
                    return image
            self.assertFalse(
                "Cloud does not have {image}".format(image=image_name))

        for image in images:
            if image.name.startswith('cirros') and image.name.endswith('-uec'):
                return image
        for image in images:
            if (image.name.startswith('cirros')
                    and image.disk_format == 'qcow2'):
                return image
        for image in images:
            if image.name.lower().startswith('ubuntu'):
                return image
        for image in images:
            if image.name.lower().startswith('centos'):
                return image
        self.assertFalse('no sensible image available')

    def addEmptyCleanup(self, func, *args, **kwargs):
        def cleanup():
            result = func(*args, **kwargs)
            self.assertIsNone(result)
        self.addCleanup(cleanup)

    # TODO(shade) Replace this with call to conn.has_service when we've merged
    #             the shade methods into Connection.
    def require_service(self, service_type, min_microversion=None, **kwargs):
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
            data = self.conn.session.get_endpoint_data(
                service_type=service_type, **kwargs)
        except _exceptions.EndpointNotFound:
            self.skipTest('Service {service_type} not found in cloud'.format(
                service_type=service_type))

        if not min_microversion:
            return

        if not (data.min_microversion
                and data.max_microversion
                and discover.version_between(
                    data.min_microversion,
                    data.max_microversion,
                    min_microversion)):
            self.skipTest('Service {service_type} does not provide '
                          'microversion {ver}'.format(
                              service_type=service_type,
                              ver=min_microversion))


class KeystoneBaseFunctionalTest(BaseFunctionalTest):

    def setUp(self):
        super(KeystoneBaseFunctionalTest, self).setUp()

        use_keystone_v2 = os.environ.get('OPENSTACKSDK_USE_KEYSTONE_V2', False)
        if use_keystone_v2:
            # keystone v2 has special behavior for the admin
            # interface and some of the operations, so make a new cloud
            # object with interface set to admin.
            # We only do it for keystone tests on v2 because otherwise
            # the admin interface is not a thing that wants to actually
            # be used
            self._set_operator_cloud(interface='admin')
