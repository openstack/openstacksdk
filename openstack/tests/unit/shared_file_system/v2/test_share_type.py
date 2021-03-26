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

from openstack.shared_file_system.v2 import share_type
from openstack.tests.unit import base


IDENTIFIER = '52a6d881-ba4e-4c50-aa0c-041e4e3756aa'
EXAMPLE = {
    "required_extra_specs": {"driver_handles_share_servers": "True"},
    "share_type_access:is_public": True,
    "extra_specs": {"driver_handles_share_servers": "True"},
    "id": IDENTIFIER,
    "name": "default-share-type",
    "is_default": True,
    "description": "manila share type",
}


class TestShareType(base.TestCase):
    def test_basic(self):
        types = share_type.ShareType()
        self.assertEqual('share_types', types.resources_key)
        self.assertEqual('/types', types.base_path)
        self.assertTrue(types.allow_list)
        self.assertTrue(types.allow_fetch)
        self.assertTrue(types.allow_commit)
        self.assertTrue(types.allow_delete)
        self.assertTrue(types.allow_create)
        self.assertFalse(types.allow_head)

        self.assertDictEqual(
            {
                'is_public': 'is_public',
                'extra_specs': 'extra_specs',
                'limit': 'limit',
                'marker': 'marker',
            },
            types._query_mapping._mapping,
        )

    def test_share_type(self):
        types = share_type.ShareType(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], types.id)
        self.assertEqual(EXAMPLE['name'], types.name)
        self.assertEqual(EXAMPLE['extra_specs'], types.extra_specs)
        self.assertEqual(
            EXAMPLE['required_extra_specs'], types.required_extra_specs
        )
        self.assertEqual(EXAMPLE['description'], types.description)
        self.assertEqual(EXAMPLE['is_default'], types.is_default)
        self.assertEqual(
            EXAMPLE['share_type_access:is_public'], types.is_public
        )

    def test_set_extra_specs(self):
        sot = share_type.ShareType(**EXAMPLE)
        specs = {'a': 'b', 'c': 'd'}

        response = mock.Mock()
        response.status_code = 200
        response.json.return_value = {'extra_specs': specs}
        sess = mock.Mock()
        sess.post.return_value = response

        result = sot.set_extra_specs(sess, **specs)

        sess.post.assert_called_once_with(
            f'types/{IDENTIFIER}/extra_specs',
            json={"extra_specs": specs},
            microversion=sess.default_microversion,
        )
        self.assertIsInstance(result, share_type.ShareType)
        self.assertEqual(specs, result.extra_specs)

    def test_delete_extra_specs(self):
        sot = share_type.ShareType(**EXAMPLE)

        sess = mock.Mock()
        response = mock.Mock()
        response.status_code = 200
        sess.delete.return_value = response

        sot.delete_extra_specs_property(sess, 'a')

        sess.delete.assert_called_once_with(
            f'types/{IDENTIFIER}/extra_specs/a',
            microversion=sess.default_microversion,
        )
