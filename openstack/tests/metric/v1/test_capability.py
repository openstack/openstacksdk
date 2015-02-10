# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock
import testtools

from openstack.metric.v1 import capability

EXAMPLE = {
    "id": "123",
    "value": False,
}
BODY = {
    "aggregation_methods": ['mean', 'max', 'avg'],
}


class TestCapability(testtools.TestCase):
    def test_basic(self):
        sot = capability.Capability()
        self.assertEqual('/capabilities', sot.base_path)
        self.assertEqual('metric', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = capability.Capability(EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['value'], sot.value)

    def test_list(self):
        sess = mock.Mock()
        resp = mock.Mock()
        resp.body = BODY
        sess.get = mock.Mock(return_value=resp)

        caps = capability.Capability.list(sess)

        caps = sorted(caps, key=lambda cap: cap.id)
        self.assertEqual(1, len(caps))
        self.assertEqual('aggregation_methods', caps[0].id)
        self.assertEqual(['mean', 'max', 'avg'], caps[0].value)
