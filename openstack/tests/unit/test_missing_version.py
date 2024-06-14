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

import warnings

import testtools

from openstack import exceptions
from openstack import proxy
from openstack.tests.unit import base


class TestMissingVersion(base.TestCase):
    def setUp(self):
        super().setUp()
        self.os_fixture.clear_tokens()
        svc = self.os_fixture.v3_token.add_service('image')
        svc.add_endpoint(
            url='https://example.com/image/',
            region='RegionOne',
            interface='public',
        )
        self.use_keystone_v3()
        self.use_glance(
            image_version_json='bad-glance-version.json',
            image_discovery_url='https://example.com/image/',
        )

    def test_unsupported_version(self):
        with testtools.ExpectedException(exceptions.NotSupported):
            self.cloud.image.get('/')

        self.assert_calls()

    def test_unsupported_version_override(self):
        self.cloud.config.config['image_api_version'] = '7'
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warnings.simplefilter("ignore", DeprecationWarning)
            self.assertIsInstance(self.cloud.image, proxy.Proxy)
            self.assertEqual(1, len(w))
            self.assertIn(
                "Service image has no discoverable version.",
                str(w[-1].message),
            )
        self.assert_calls()
