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

from openstack.tests.unit import base

from openstack.clustering.v1 import build_info


FAKE = {
    'api': {
        'revision': '1.0.0',
    },
    'engine': {
        'revision': '1.0.0',
    }
}


class TestBuildInfo(base.TestCase):

    def setUp(self):
        super(TestBuildInfo, self).setUp()

    def test_basic(self):
        sot = build_info.BuildInfo()
        self.assertEqual('/build-info', sot.base_path)
        self.assertEqual('build_info', sot.resource_key)
        self.assertEqual('clustering', sot.service.service_type)
        self.assertTrue(sot.allow_get)

    def test_instantiate(self):
        sot = build_info.BuildInfo(**FAKE)
        self.assertEqual(FAKE['api'], sot.api)
        self.assertEqual(FAKE['engine'], sot.engine)
