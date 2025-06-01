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

from unittest import mock
import uuid

import testtools

from openstack.config import cloud_region
from openstack import exceptions
from openstack.tests import fakes
from openstack.tests.unit import base


class TestOperatorCloud(base.TestCase):
    def test_get_image_name(self):
        self.use_glance()

        image_id = self.getUniqueString()
        fake_image = fakes.make_fake_image(image_id=image_id)
        list_return = {'images': [fake_image]}

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://image.example.com/v2/images',
                    json=list_return,
                ),
                dict(
                    method='GET',
                    uri='https://image.example.com/v2/images',
                    json=list_return,
                ),
            ]
        )

        self.assertEqual('fake_image', self.cloud.get_image_name(image_id))
        self.assertEqual('fake_image', self.cloud.get_image_name('fake_image'))

        self.assert_calls()

    def test_get_image_id(self):
        self.use_glance()

        image_id = self.getUniqueString()
        fake_image = fakes.make_fake_image(image_id=image_id)
        list_return = {'images': [fake_image]}

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://image.example.com/v2/images',
                    json=list_return,
                ),
                dict(
                    method='GET',
                    uri='https://image.example.com/v2/images',
                    json=list_return,
                ),
            ]
        )

        self.assertEqual(image_id, self.cloud.get_image_id(image_id))
        self.assertEqual(image_id, self.cloud.get_image_id('fake_image'))

        self.assert_calls()

    @mock.patch.object(cloud_region.CloudRegion, 'get_session')
    def test_get_session_endpoint_exception(self, get_session_mock):
        class FakeException(Exception):
            pass

        def side_effect(*args, **kwargs):
            raise FakeException("No service")

        session_mock = mock.Mock()
        session_mock.get_endpoint.side_effect = side_effect
        get_session_mock.return_value = session_mock
        self.cloud.name = 'testcloud'
        self.cloud.config.config['region_name'] = 'testregion'
        with testtools.ExpectedException(
            exceptions.SDKException,
            "Error getting image endpoint on testcloud:testregion: No service",
        ):
            self.cloud.get_session_endpoint("image")

    @mock.patch.object(cloud_region.CloudRegion, 'get_session')
    def test_get_session_endpoint_unavailable(self, get_session_mock):
        session_mock = mock.Mock()
        session_mock.get_endpoint.return_value = None
        get_session_mock.return_value = session_mock
        image_endpoint = self.cloud.get_session_endpoint("image")
        self.assertIsNone(image_endpoint)

    @mock.patch.object(cloud_region.CloudRegion, 'get_session')
    def test_get_session_endpoint_identity(self, get_session_mock):
        session_mock = mock.Mock()
        get_session_mock.return_value = session_mock
        self.cloud.get_session_endpoint('identity')
        kwargs = dict(
            service_type='identity',
            region_name='RegionOne',
            interface='public',
            service_name=None,
            min_version=None,
            max_version=None,
        )

        session_mock.get_endpoint.assert_called_with(**kwargs)

    @mock.patch.object(cloud_region.CloudRegion, 'get_session')
    def test_has_service_no(self, get_session_mock):
        session_mock = mock.Mock()
        session_mock.get_endpoint.return_value = None
        get_session_mock.return_value = session_mock
        self.assertFalse(self.cloud.has_service("image"))

    @mock.patch.object(cloud_region.CloudRegion, 'get_session')
    def test_has_service_yes(self, get_session_mock):
        session_mock = mock.Mock()
        session_mock.get_endpoint.return_value = 'http://fake.url'
        get_session_mock.return_value = session_mock
        self.assertTrue(self.cloud.has_service("image"))

    def test_list_hypervisors(self):
        '''This test verifies that calling list_hypervisors results in a call
        to nova client.'''
        uuid1 = uuid.uuid4().hex
        uuid2 = uuid.uuid4().hex
        self.use_compute_discovery()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://compute.example.com/v2.1/os-hypervisors/detail',  # noqa: E501
                    json={
                        'hypervisors': [
                            fakes.make_fake_hypervisor(uuid1, 'testserver1'),
                            fakes.make_fake_hypervisor(uuid2, 'testserver2'),
                        ]
                    },
                    validate={
                        'headers': {'OpenStack-API-Version': 'compute 2.53'}
                    },
                ),
            ]
        )

        r = self.cloud.list_hypervisors()

        self.assertEqual(2, len(r))
        self.assertEqual('testserver1', r[0]['name'])
        self.assertEqual(uuid1, r[0]['id'])
        self.assertEqual('testserver2', r[1]['name'])
        self.assertEqual(uuid2, r[1]['id'])

        self.assert_calls()

    def test_list_old_hypervisors(self):
        '''This test verifies that calling list_hypervisors on a pre-2.53 cloud
        calls the old version.'''
        self.use_compute_discovery(
            compute_version_json='old-compute-version.json'
        )
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri='https://compute.example.com/v2.1/os-hypervisors/detail',  # noqa: E501
                    json={
                        'hypervisors': [
                            fakes.make_fake_hypervisor('1', 'testserver1'),
                            fakes.make_fake_hypervisor('2', 'testserver2'),
                        ]
                    },
                ),
            ]
        )

        r = self.cloud.list_hypervisors()

        self.assertEqual(2, len(r))
        self.assertEqual('testserver1', r[0]['name'])
        self.assertEqual('testserver2', r[1]['name'])

        self.assert_calls()
