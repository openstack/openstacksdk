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

from openstack.identity import version
from openstack.tests.unit import base

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'media-types': '2',
    'status': '3',
    'updated': '4',
}


class TestVersion(base.TestCase):

    def test_basic(self):
        sot = version.Version()
        self.assertEqual('version', sot.resource_key)
        self.assertEqual('versions', sot.resources_key)
        self.assertEqual('/', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = version.Version(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['media-types'], sot.media_types)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['updated'], sot.updated)

    def test_list(self):
        resp = mock.Mock()
        resp.body = {
            "versions": {
                "values": [
                    {"status": "stable", "updated": "a", "id": "v1.0"},
                    {"status": "stable", "updated": "b", "id": "v1.1"},
                ]
            }
        }
        resp.json = mock.Mock(return_value=resp.body)
        session = mock.Mock()
        session.get = mock.Mock(return_value=resp)
        sot = version.Version(**EXAMPLE)
        result = sot.list(session)
        self.assertEqual(next(result).id, 'v1.0')
        self.assertEqual(next(result).id, 'v1.1')
        self.assertRaises(StopIteration, next, result)
