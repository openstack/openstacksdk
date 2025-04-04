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

import operator
import os
import time
import uuid

from keystoneauth1 import discover

import openstack.config
from openstack import connection
from openstack.tests import base


#: Defines the OpenStack Client Config (OCC) cloud key in your OCC config
#: file, typically in $HOME/.config/openstack/clouds.yaml. That configuration
#: will determine where the functional tests will be run and what resource
#: defaults will be used to run the functional tests.
TEST_CONFIG = openstack.config.OpenStackConfig()
TEST_CLOUD_NAME = os.getenv('OS_CLOUD', 'devstack-admin')
TEST_CLOUD_REGION = openstack.config.get_cloud_region(cloud=TEST_CLOUD_NAME)


def _get_resource_value(resource_key):
    return TEST_CONFIG.get_extra_config('functional').get(resource_key)


def _disable_keep_alive(conn):
    sess = conn.config.get_session()
    sess.keep_alive = False


class BaseFunctionalTest(base.TestCase):
    user_cloud: connection.Connection
    user_cloud_alt: connection.Connection
    operator_cloud: connection.Connection

    _wait_for_timeout_key = ''

    def setUp(self):
        super().setUp()

        self._system_admin_name = os.environ.get(
            'OPENSTACKSDK_SYSTEM_ADMIN_CLOUD',
            'devstack-system-admin',
        )
        if not self._system_admin_name:
            raise self.failureException(
                "OPENSTACKSDK_SYSTEM_ADMIN_CLOUD must be set to a non-empty "
                "value"
            )

        self.config = openstack.config.OpenStackConfig()

        self._user_cloud_name = os.environ.get(
            'OPENSTACKSDK_DEMO_CLOUD', 'devstack'
        )
        if not self._user_cloud_name:
            raise self.failureException(
                "OPENSTACKSDK_DEMO_CLOUD must be set to a non-empty value"
            )

        self._user_alt_cloud_name = os.environ.get(
            'OPENSTACKSDK_DEMO_CLOUD_ALT', 'devstack-alt'
        )
        if not self._user_alt_cloud_name:
            raise self.failureException(
                "OPENSTACKSDK_DEMO_CLOUD_ALT must be set to a non-empty value"
            )

        self._set_user_cloud()

        self._operator_cloud_name = os.environ.get(
            'OPENSTACKSDK_OPERATOR_CLOUD', 'devstack-admin'
        )
        if not self._operator_cloud_name:
            raise self.failureException(
                "OPENSTACKSDK_OPERATOR_CLOUD must be set to a non-empty value"
            )

        self._set_operator_cloud()

        self.flavor = self._pick_flavor()
        self.image = self._pick_image()

        # Defines default timeout for wait_for methods used
        # in the functional tests
        self._wait_for_timeout = int(
            os.getenv(
                self._wait_for_timeout_key,
                os.getenv('OPENSTACKSDK_FUNC_TEST_TIMEOUT', 300),
            )
        )

    def _set_user_cloud(self, **kwargs):
        user_config = self.config.get_one(
            cloud=self._user_cloud_name, **kwargs
        )
        self.user_cloud = connection.Connection(config=user_config)
        _disable_keep_alive(self.user_cloud)

        user_config_alt = self.config.get_one(
            cloud=self._user_alt_cloud_name, **kwargs
        )
        self.user_cloud_alt = connection.Connection(config=user_config_alt)
        _disable_keep_alive(self.user_cloud_alt)

    def _set_operator_cloud(self, **kwargs):
        operator_config = self.config.get_one(
            cloud=self._operator_cloud_name, **kwargs
        )
        self.operator_cloud = connection.Connection(config=operator_config)
        _disable_keep_alive(self.operator_cloud)

        system_admin_config = self.config.get_one(
            cloud=self._system_admin_name, **kwargs
        )
        self.system_admin_cloud = connection.Connection(
            config=system_admin_config
        )
        _disable_keep_alive(self.system_admin_cloud)

    def _pick_flavor(self):
        """Pick a sensible flavor to run tests with.

        This returns None if the compute service is not present (e.g.
        ironic-only deployments).
        """
        if not self.user_cloud.has_service('compute'):
            return None

        flavors = self.user_cloud.list_flavors(get_extra=False)

        flavor_name = os.environ.get('OPENSTACKSDK_FLAVOR')

        if not flavor_name:
            flavor_name = _get_resource_value('flavor_name')

        if flavor_name:
            for flavor in flavors:
                if flavor.name == flavor_name:
                    return flavor

            raise self.failureException(
                "Cloud does not have flavor '%s'",
                flavor_name,
            )

        # Enable running functional tests against RAX, which requires
        # performance flavors be used for boot from volume

        for flavor in sorted(flavors, key=operator.attrgetter('ram')):
            if 'performance' in flavor.name:
                return flavor

        # Otherwise, pick the smallest flavor with a ephemeral disk configured

        for flavor in sorted(flavors, key=operator.attrgetter('ram')):
            if flavor.disk:
                return flavor

        raise self.failureException('No sensible flavor found')

    def _pick_image(self):
        """Pick a sensible image to run tests with.

        This returns None if the image service is not present.
        """
        if not self.user_cloud.has_service('image'):
            return None

        images = self.user_cloud.list_images()

        image_name = os.environ.get('OPENSTACKSDK_IMAGE')

        if not image_name:
            image_name = _get_resource_value('image_name')

        if image_name:
            for image in images:
                if image.name == image_name:
                    return image

            raise self.failureException(
                "Cloud does not have image '%s'",
                image_name,
            )

        for image in images:
            if image.name.startswith('cirros') and image.name.endswith('-uec'):
                return image

        for image in images:
            if (
                image.name.startswith('cirros')
                and image.disk_format == 'qcow2'
            ):
                return image

        for image in images:
            if image.name.lower().startswith('ubuntu'):
                return image
        for image in images:
            if image.name.lower().startswith('centos'):
                return image

        raise self.failureException('No sensible image found')

    def addEmptyCleanup(self, func, *args, **kwargs):
        def cleanup():
            result = func(*args, **kwargs)
            self.assertIsNone(result)

        self.addCleanup(cleanup)

    def require_service(self, service_type, min_microversion=None, **kwargs):
        """Method to check whether a service exists

        Usage::

            class TestMeter(base.BaseFunctionalTest):
                def setUp(self):
                    super(TestMeter, self).setUp()
                    self.require_service('metering')

        :returns: True if the service exists, otherwise False.
        """
        if not self.operator_cloud.has_service(service_type):
            self.skipTest(f'Service {service_type} not found in cloud')

        if not min_microversion:
            return

        data = self.operator_cloud.session.get_endpoint_data(
            service_type=service_type, **kwargs
        )

        if not (
            data.min_microversion
            and data.max_microversion
            and discover.version_between(
                data.min_microversion,
                data.max_microversion,
                min_microversion,
            )
        ):
            self.skipTest(
                f'Service {service_type} does not provide microversion '
                f'{min_microversion}'
            )

    def getUniqueString(self, prefix=None):
        """Generate unique resource name"""
        # Globally unique names can only rely on some form of uuid
        # unix_t is also used to easier determine orphans when running real
        # functional tests on a real cloud
        return (
            prefix if prefix else ''
        ) + f"{int(time.time())}-{uuid.uuid4().hex}"

    def create_temporary_project(self):
        """Create a new temporary project.

        This is useful for tests that modify things like quotas, which would
        cause issues for other tests.
        """
        project_name = self.getUniqueString('project-')
        project = self.operator_cloud.get_project(project_name)
        if not project:
            params = {
                'name': project_name,
                'description': f'Temporary project created for {self.id()}',
                # assume identity API v3 for now
                'domain_id': self.operator_cloud.get_domain('default')['id'],
            }
            project = self.operator_cloud.create_project(**params)

        # Grant the current user access to the project
        user_id = self.operator_cloud.current_user_id
        role_assignment = self.operator_cloud.list_role_assignments(
            {'user': user_id, 'project': project['id']}
        )
        if not role_assignment:
            self.operator_cloud.grant_role(
                'member', user=user_id, project=project['id'], wait=True
            )

        self.addCleanup(self._delete_temporary_project, project)

        return project

    def _delete_temporary_project(self, project):
        self.operator_cloud.revoke_role(
            'member',
            user=self.operator_cloud.current_user_id,
            project=project.id,
        )
        self.operator_cloud.delete_project(project.id)


class KeystoneBaseFunctionalTest(BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        # we only support v3, since v2 was deprecated in Queens (2018)

        if not self.user_cloud.has_service('identity', '3'):
            self.skipTest('identity service not supported by cloud')
