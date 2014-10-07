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

import mock
import six
import testtools

from openstack.compute.v2 import limits_absolute

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'name': 'maxImageMeta',
    'value': '2',
}
FAKE_RESPONSES = {
    "limits": {
        "absolute": {
            "maxImageMeta": 128,
            "maxPersonality": 5,
            "maxPersonalitySize": 10240,
            "maxSecurityGroupRules": 20,
            "maxSecurityGroups": 10,
            "maxServerMeta": 128,
            "maxTotalCores": 20,
            "maxTotalFloatingIps": 10,
            "maxTotalInstances": 10,
            "maxTotalKeypairs": 100,
            "maxTotalRAMSize": 51200,
        }
    }
}


class TestLimitsAbsolute(testtools.TestCase):

    def test_basic(self):
        sot = limits_absolute.LimitsAbsolute()
        self.assertEqual('limits_absolute', sot.resource_key)
        self.assertEqual('limits_absolutes', sot.resources_key)
        self.assertEqual('/limits', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = limits_absolute.LimitsAbsolute(EXAMPLE)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['value'], sot.value)

    def test_list(self):
        resp = mock.Mock()
        resp.body = FAKE_RESPONSES
        sess = mock.Mock()
        sess.get = mock.MagicMock()
        sess.get.return_value = resp
        sot = limits_absolute.LimitsAbsolute()

        resp = sot.list(sess)

        url = '/limits'
        sess.get.assert_called_with(url, service=sot.service, params={})
        absolute = FAKE_RESPONSES['limits']['absolute']
        cnt = 0
        for key, value in six.iteritems(absolute):
            self.assertEqual(key, resp[cnt].name)
            self.assertEqual(value, resp[cnt].value)
            cnt = cnt + 1
