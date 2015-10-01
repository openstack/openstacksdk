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

import copy

from os_client_config import cloud_config
from os_client_config.tests import base


fake_config_dict = {'a': 1, 'os_b': 2, 'c': 3, 'os_c': 4}
fake_services_dict = {
    'compute_api_version': 2,
    'compute_endpoint': 'http://compute.example.com',
    'compute_region_name': 'region-bl',
    'interface': 'public',
    'image_service_type': 'mage',
    'identity_interface': 'admin',
    'identity_service_name': 'locks',
    'auth': {'password': 'hunter2', 'username': 'AzureDiamond'},
}


class TestCloudConfig(base.TestCase):

    def test_arbitrary_attributes(self):
        cc = cloud_config.CloudConfig("test1", "region-al", fake_config_dict)
        self.assertEqual("test1", cc.name)
        self.assertEqual("region-al", cc.region)

        # Look up straight value
        self.assertEqual(1, cc.a)

        # Look up prefixed attribute, fail - returns None
        self.assertEqual(None, cc.os_b)

        # Look up straight value, then prefixed value
        self.assertEqual(3, cc.c)
        self.assertEqual(3, cc.os_c)

        # Lookup mystery attribute
        self.assertIsNone(cc.x)

        # Test default ipv6
        self.assertFalse(cc.force_ipv4)

    def test_iteration(self):
        cc = cloud_config.CloudConfig("test1", "region-al", fake_config_dict)
        self.assertTrue('a' in cc)
        self.assertFalse('x' in cc)

    def test_equality(self):
        cc1 = cloud_config.CloudConfig("test1", "region-al", fake_config_dict)
        cc2 = cloud_config.CloudConfig("test1", "region-al", fake_config_dict)
        self.assertEqual(cc1, cc2)

    def test_inequality(self):
        cc1 = cloud_config.CloudConfig("test1", "region-al", fake_config_dict)

        cc2 = cloud_config.CloudConfig("test2", "region-al", fake_config_dict)
        self.assertNotEqual(cc1, cc2)

        cc2 = cloud_config.CloudConfig("test1", "region-xx", fake_config_dict)
        self.assertNotEqual(cc1, cc2)

        cc2 = cloud_config.CloudConfig("test1", "region-al", {})
        self.assertNotEqual(cc1, cc2)

    def test_verify(self):
        config_dict = copy.deepcopy(fake_config_dict)
        config_dict['cacert'] = None

        config_dict['verify'] = False
        cc = cloud_config.CloudConfig("test1", "region-xx", config_dict)
        (verify, cert) = cc.get_requests_verify_args()
        self.assertFalse(verify)

        config_dict['verify'] = True
        cc = cloud_config.CloudConfig("test1", "region-xx", config_dict)
        (verify, cert) = cc.get_requests_verify_args()
        self.assertTrue(verify)

    def test_verify_cacert(self):
        config_dict = copy.deepcopy(fake_config_dict)
        config_dict['cacert'] = "certfile"

        config_dict['verify'] = False
        cc = cloud_config.CloudConfig("test1", "region-xx", config_dict)
        (verify, cert) = cc.get_requests_verify_args()
        self.assertFalse(verify)

        config_dict['verify'] = True
        cc = cloud_config.CloudConfig("test1", "region-xx", config_dict)
        (verify, cert) = cc.get_requests_verify_args()
        self.assertEqual("certfile", verify)

    def test_cert_with_key(self):
        config_dict = copy.deepcopy(fake_config_dict)
        config_dict['cacert'] = None
        config_dict['verify'] = False

        config_dict['cert'] = 'cert'
        config_dict['key'] = 'key'

        cc = cloud_config.CloudConfig("test1", "region-xx", config_dict)
        (verify, cert) = cc.get_requests_verify_args()
        self.assertEqual(("cert", "key"), cert)

    def test_ipv6(self):
        cc = cloud_config.CloudConfig(
            "test1", "region-al", fake_config_dict, force_ipv4=True)
        self.assertTrue(cc.force_ipv4)

    def test_getters(self):
        cc = cloud_config.CloudConfig("test1", "region-al", fake_services_dict)

        self.assertEqual(['compute', 'identity', 'image'],
                         sorted(cc.get_services()))
        self.assertEqual({'password': 'hunter2', 'username': 'AzureDiamond'},
                         cc.get_auth_args())
        self.assertEqual('public', cc.get_interface())
        self.assertEqual('public', cc.get_interface('compute'))
        self.assertEqual('admin', cc.get_interface('identity'))
        self.assertEqual('region-al', cc.get_region_name())
        self.assertEqual('region-al', cc.get_region_name('image'))
        self.assertEqual('region-bl', cc.get_region_name('compute'))
        self.assertEqual(None, cc.get_api_version('image'))
        self.assertEqual(2, cc.get_api_version('compute'))
        self.assertEqual('mage', cc.get_service_type('image'))
        self.assertEqual('compute', cc.get_service_type('compute'))
        self.assertEqual('http://compute.example.com',
                         cc.get_endpoint('compute'))
        self.assertEqual(None,
                         cc.get_endpoint('image'))
        self.assertEqual(None, cc.get_service_name('compute'))
        self.assertEqual('locks', cc.get_service_name('identity'))
