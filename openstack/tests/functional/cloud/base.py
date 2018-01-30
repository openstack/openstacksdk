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

# TODO(shade) Merge this with openstack.tests.functional.base

import os

import openstack.config as occ

from openstack import connection
from openstack.tests import base


class BaseFunctionalTestCase(base.TestCase):
    def setUp(self):
        super(BaseFunctionalTestCase, self).setUp()

        self._demo_name = os.environ.get('OPENSTACKSDK_DEMO_CLOUD', 'devstack')
        self._op_name = os.environ.get(
            'OPENSTACKSDK_OPERATOR_CLOUD', 'devstack-admin')

        self.config = occ.OpenStackConfig()
        self._set_user_cloud()
        self._set_operator_cloud()

        self.identity_version = \
            self.operator_cloud.config.get_api_version('identity')

    def _set_user_cloud(self, **kwargs):
        user_config = self.config.get_one(
            cloud=self._demo_name, **kwargs)
        self.user_cloud = connection.Connection(config=user_config)

    def _set_operator_cloud(self, **kwargs):
        operator_config = self.config.get_one(
            cloud=self._op_name, **kwargs)
        self.operator_cloud = connection.Connection(config=operator_config)

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


class KeystoneBaseFunctionalTestCase(BaseFunctionalTestCase):

    def setUp(self):
        super(KeystoneBaseFunctionalTestCase, self).setUp()

        use_keystone_v2 = os.environ.get('OPENSTACKSDK_USE_KEYSTONE_V2', False)
        if use_keystone_v2:
            # keystone v2 has special behavior for the admin
            # interface and some of the operations, so make a new cloud
            # object with interface set to admin.
            # We only do it for keystone tests on v2 because otherwise
            # the admin interface is not a thing that wants to actually
            # be used
            self._set_operator_cloud(interface='admin')
