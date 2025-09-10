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

from keystoneauth1 import adapter

from openstack.dns.v2 import tld
from openstack.tests.unit import base

IDENTIFIER = "NAME"
EXAMPLE = {
    "id": IDENTIFIER,
    "name": "com",
    "description": "tld description",
}


class TestTLD(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.status_code = 200
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess.default_microversion = None

    def test_basic(self):
        sot = tld.TLD()
        self.assertEqual(None, sot.resource_key)
        self.assertEqual("tlds", sot.resources_key)
        self.assertEqual("/tlds", sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)

        self.assertEqual("PATCH", sot.commit_method)

        self.assertDictEqual(
            {
                "description": "description",
                "name": "name",
                "limit": "limit",
                "marker": "marker",
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = tld.TLD(**EXAMPLE)
        self.assertEqual(IDENTIFIER, sot.id)
        self.assertEqual(EXAMPLE["description"], sot.description)
        self.assertEqual(EXAMPLE["name"], sot.name)
