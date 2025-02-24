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

from openstack import exceptions
from openstack.tests import fakes
from openstack.tests.unit import base


class TestMicroversions(base.TestCase):
    def setUp(self):
        super().setUp()
        self.use_compute_discovery()

    def test_get_bad_inferred_max_microversion(self):
        self.cloud.config.config['compute_api_version'] = '2.61'

        self.assertRaises(
            exceptions.ConfigException,
            self.cloud.get_server,
            'doesNotExist',
        )

        self.assert_calls()

    def test_get_bad_default_max_microversion(self):
        self.cloud.config.config['compute_default_microversion'] = '2.61'

        self.assertRaises(
            exceptions.ConfigException,
            self.cloud.get_server,
            'doesNotExist',
        )

        self.assert_calls()

    def test_get_bad_inferred_min_microversion(self):
        self.cloud.config.config['compute_api_version'] = '2.7'

        self.assertRaises(
            exceptions.ConfigException,
            self.cloud.get_server,
            'doesNotExist',
        )

        self.assert_calls()

    def test_get_bad_default_min_microversion(self):
        self.cloud.config.config['compute_default_microversion'] = '2.7'

        self.assertRaises(
            exceptions.ConfigException,
            self.cloud.get_server,
            'doesNotExist',
        )

        self.assert_calls()

    def test_inferred_default_microversion(self):
        self.cloud.config.config['compute_api_version'] = '2.42'

        server = fakes.make_fake_server('123', 'mickey')

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', 'mickey']
                    ),
                    request_headers={'OpenStack-API-Version': 'compute 2.42'},
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'detail'],
                        qs_elements=['name=mickey'],
                    ),
                    request_headers={'OpenStack-API-Version': 'compute 2.42'},
                    json={'servers': [server]},
                ),
            ]
        )

        r = self.cloud.get_server('mickey', bare=True)
        self.assertIsNotNone(r)
        self.assertEqual(server['name'], r['name'])

        self.assert_calls()

    def test_default_microversion(self):
        self.cloud.config.config['compute_default_microversion'] = '2.42'

        server = fakes.make_fake_server('123', 'mickey')

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute', 'public', append=['servers', 'mickey']
                    ),
                    request_headers={'OpenStack-API-Version': 'compute 2.42'},
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'compute',
                        'public',
                        append=['servers', 'detail'],
                        qs_elements=['name=mickey'],
                    ),
                    request_headers={'OpenStack-API-Version': 'compute 2.42'},
                    json={'servers': [server]},
                ),
            ]
        )

        r = self.cloud.get_server('mickey', bare=True)
        self.assertIsNotNone(r)
        self.assertEqual(server['name'], r['name'])

        self.assert_calls()

    def test_conflicting_implied_and_direct(self):
        self.cloud.config.config['compute_default_microversion'] = '2.7'
        self.cloud.config.config['compute_api_version'] = '2.13'

        self.assertRaises(exceptions.ConfigException, self.cloud.get_server)

        # We should fail before we even authenticate
        self.assertEqual(0, len(self.adapter.request_history))
