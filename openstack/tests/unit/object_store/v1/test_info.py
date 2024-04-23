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

from openstack.object_store.v1 import info
from openstack.tests.unit import base


class TestInfo(base.TestCase):
    def setUp(self):
        super().setUp()

    def test_get_info_url(self):
        sot = info.Info()
        test_urls = {
            'http://object.cloud.example.com': 'http://object.cloud.example.com/info',
            'http://object.cloud.example.com/': 'http://object.cloud.example.com/info',
            'http://object.cloud.example.com/v1': 'http://object.cloud.example.com/info',
            'http://object.cloud.example.com/v1/': 'http://object.cloud.example.com/info',
            'http://object.cloud.example.com/swift': 'http://object.cloud.example.com/swift/info',
            'http://object.cloud.example.com/swift/': 'http://object.cloud.example.com/swift/info',
            'http://object.cloud.example.com/v1.0': 'http://object.cloud.example.com/info',
            'http://object.cloud.example.com/swift/v1.0': 'http://object.cloud.example.com/swift/info',
            'http://object.cloud.example.com/v111': 'http://object.cloud.example.com/info',
            'http://object.cloud.example.com/v111/test': 'http://object.cloud.example.com/info',
            'http://object.cloud.example.com/v1/test': 'http://object.cloud.example.com/info',
            'http://object.cloud.example.com/swift/v1.0/test': 'http://object.cloud.example.com/swift/info',
            'http://object.cloud.example.com/v1.0/test': 'http://object.cloud.example.com/info',
            'https://object.cloud.example.com/swift/v1/AUTH_%(tenant_id)s': 'https://object.cloud.example.com/swift/info',
            'https://object.cloud.example.com/swift/v1/AUTH_%(project_id)s': 'https://object.cloud.example.com/swift/info',
            'https://object.cloud.example.com/services/swift/v1/AUTH_%(project_id)s': 'https://object.cloud.example.com/services/swift/info',
            'https://object.cloud.example.com/services/swift/v1/AUTH_%(project_id)s/': 'https://object.cloud.example.com/services/swift/info',
            'https://object.cloud.example.com/info/v1/AUTH_%(project_id)s/': 'https://object.cloud.example.com/info/info',
        }
        for uri_k, uri_v in test_urls.items():
            self.assertEqual(sot._get_info_url(uri_k), uri_v)
