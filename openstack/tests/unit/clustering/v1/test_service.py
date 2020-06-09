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

from unittest import mock

from openstack.clustering.v1 import service
from openstack.tests.unit import base

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'binary': 'senlin-engine',
    'host': 'host1',
    'status': 'enabled',
    'state': 'up',
    'disabled_reason': None,
    'updated_at': '2016-10-10T12:46:36.000000',
}


class TestService(base.TestCase):

    def setUp(self):
        super(TestService, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock()
        self.sess.put = mock.Mock(return_value=self.resp)

    def test_basic(self):
        sot = service.Service()
        self.assertEqual('service', sot.resource_key)
        self.assertEqual('services', sot.resources_key)
        self.assertEqual('/services', sot.base_path)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = service.Service(**EXAMPLE)
        self.assertEqual(EXAMPLE['host'], sot.host)
        self.assertEqual(EXAMPLE['binary'], sot.binary)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['state'], sot.state)
        self.assertEqual(EXAMPLE['disabled_reason'], sot.disabled_reason)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
