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

import testtools

from openstack.metric.v1 import capabilities

BODY = {
    'aggregation_methods': ['mean', 'max', 'avg'],
}


class TestCapabilites(testtools.TestCase):
    def test_basic(self):
        sot = capabilities.Capabilities()
        self.assertEqual('/capabilities', sot.base_path)
        self.assertEqual('metric', sot.service.service_type)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = capabilities.Capabilities(BODY)
        self.assertEqual(BODY['aggregation_methods'],
                         sot.aggregation_methods)
