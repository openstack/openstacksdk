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


from os_client_config import cloud_config
from os_client_config.tests import base


fake_config_dict = {'a': 1, 'os_b': 2, 'c': 3, 'os_c': 4}


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
