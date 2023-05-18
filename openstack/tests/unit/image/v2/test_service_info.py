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

from openstack import exceptions
from openstack.image.v2 import service_info as si
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE_IMPORT = {
    'import-methods': {
        'description': 'Import methods available.',
        'type': 'array',
        'value': ['glance-direct', 'web-download'],
    }
}
EXAMPLE_STORE = {
    'id': IDENTIFIER,
    'description': 'Fast access to rbd store',
    'default': True,
    'properties': {
        "pool": "pool1",
        "chunk_size": 65536,
        "thin_provisioning": False,
    },
}


class TestStore(base.TestCase):
    def test_basic(self):
        sot = si.Store()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('stores', sot.resources_key)
        self.assertEqual('/info/stores', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = si.Store(**EXAMPLE_STORE)
        self.assertEqual(EXAMPLE_STORE['id'], sot.id)
        self.assertEqual(EXAMPLE_STORE['description'], sot.description)
        self.assertEqual(EXAMPLE_STORE['default'], sot.is_default)
        self.assertEqual(EXAMPLE_STORE['properties'], sot.properties)

    @mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
    def test_delete_image(self):
        sot = si.Store(**EXAMPLE_STORE)
        session = mock.Mock()
        session.delete = mock.Mock()

        sot.delete_image(session, image='image_id')

        session.delete.assert_called_with('stores/IDENTIFIER/image_id')


class TestImport(base.TestCase):
    def test_basic(self):
        sot = si.Import()
        self.assertIsNone(sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/info/import', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = si.Import(**EXAMPLE_IMPORT)
        self.assertEqual(EXAMPLE_IMPORT['import-methods'], sot.import_methods)
