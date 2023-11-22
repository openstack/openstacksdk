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

from openstack import exceptions
from openstack.image.v2 import metadef_namespace
from openstack.tests.unit import base


EXAMPLE = {
    'display_name': 'Cinder Volume Type',
    'created_at': '2022-08-24T17:46:24Z',
    'protected': True,
    'namespace': 'OS::Cinder::Volumetype',
    'description': (
        'The Cinder volume type configuration option. Volume type '
        'assignment provides a mechanism not only to provide scheduling to a '
        'specific storage back-end, but also can be used to specify specific '
        'information for a back-end storage device to act upon.'
    ),
    'visibility': 'public',
    'owner': 'admin',
    'resource_type_associations': [
        {
            'name': 'OS::Glance::Image',
            'prefix': 'cinder_',
            'created_at': '2022-08-24T17:46:24Z',
        },
    ],
}


class TestMetadefNamespace(base.TestCase):
    def test_basic(self):
        sot = metadef_namespace.MetadefNamespace()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('namespaces', sot.resources_key)
        self.assertEqual('/metadefs/namespaces', sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_delete)

    def test_make_it(self):
        sot = metadef_namespace.MetadefNamespace(**EXAMPLE)
        self.assertEqual(EXAMPLE['namespace'], sot.namespace)
        self.assertEqual(EXAMPLE['visibility'], sot.visibility)
        self.assertEqual(EXAMPLE['owner'], sot.owner)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['protected'], sot.is_protected)
        self.assertEqual(EXAMPLE['display_name'], sot.display_name)
        self.assertEqual(
            EXAMPLE['resource_type_associations'],
            sot.resource_type_associations,
        )
        self.assertDictEqual(
            {
                'limit': 'limit',
                'marker': 'marker',
                'resource_types': 'resource_types',
                'sort_dir': 'sort_dir',
                'sort_key': 'sort_key',
                'visibility': 'visibility',
            },
            sot._query_mapping._mapping,
        )

    @mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
    def test_delete_all_properties(self):
        sot = metadef_namespace.MetadefNamespace(**EXAMPLE)
        session = mock.Mock(spec=adapter.Adapter)
        sot._translate_response = mock.Mock()
        sot.delete_all_properties(session)
        session.delete.assert_called_with(
            'metadefs/namespaces/OS::Cinder::Volumetype/properties'
        )

    @mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
    def test_delete_all_objects(self):
        sot = metadef_namespace.MetadefNamespace(**EXAMPLE)
        session = mock.Mock(spec=adapter.Adapter)
        sot._translate_response = mock.Mock()
        sot.delete_all_objects(session)
        session.delete.assert_called_with(
            'metadefs/namespaces/OS::Cinder::Volumetype/objects'
        )
