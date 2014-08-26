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
import testtools

from openstack.compute.v2 import limits_rate

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'limit': '1',
    'regex': '2',
    'uri': '3',
}
FAKE_RESPONSES = {
    "limits": {
        "rate": [
            {
                "limit": "1",
                "regex": ".*",
                "uri": "*"
            },
            {
                "limit": "2",
                "regex": "^/servers",
                "uri": "*/servers"
            },
        ]
    }
}


class TestLimitsRate(testtools.TestCase):

    def test_basic(self):
        sot = limits_rate.LimitsRate()
        self.assertEqual('limits_rate', sot.resource_key)
        self.assertEqual('limits_rates', sot.resources_key)
        self.assertEqual('/limits', sot.base_path)
        self.assertEqual('compute', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = limits_rate.LimitsRate(EXAMPLE)
        self.assertEqual(EXAMPLE['limit'], sot.limit)
        self.assertEqual(EXAMPLE['regex'], sot.regex)
        self.assertEqual(EXAMPLE['uri'], sot.uri)

    def test_list(self):
        resp = mock.Mock()
        resp.body = FAKE_RESPONSES
        sess = mock.Mock()
        sess.get = mock.MagicMock()
        sess.get.return_value = resp
        sot = limits_rate.LimitsRate()

        resp = sot.list(sess)

        url = '/limits'
        sess.get.assert_called_with(url, service=sot.service, params={})
        rate = FAKE_RESPONSES['limits']['rate']
        cnt = 0
        for value in rate:
            self.assertEqual(value['limit'], resp[cnt].limit)
            self.assertEqual(value['regex'], resp[cnt].regex)
            self.assertEqual(value['uri'], resp[cnt].uri)
            cnt = cnt + 1
