# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import random
import string

from openstack.image.v2 import metadef_namespace as _metadef_namespace
from openstack.image.v2 import metadef_property as _metadef_property
from openstack.tests.functional.image.v2 import base


class TestMetadefProperty(base.BaseImageTest):
    def setUp(self):
        super().setUp()

        # there's a limit on namespace length
        namespace = 'test_' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(75)
        )
        self.metadef_namespace = (
            self.operator_cloud.image.create_metadef_namespace(
                namespace=namespace,
            )
        )
        self.assertIsInstance(
            self.metadef_namespace,
            _metadef_namespace.MetadefNamespace,
        )
        self.assertEqual(namespace, self.metadef_namespace.namespace)

        # there's a limit on property length
        property_name = 'test_' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(75)
        )
        self.attrs = {
            'name': property_name,
            'title': property_name,
            'type': 'string',
            'description': 'Web Server port',
            'enum': ["80", "443"],
        }
        self.metadef_property = (
            self.operator_cloud.image.create_metadef_property(
                self.metadef_namespace.namespace, **self.attrs
            )
        )
        self.assertIsInstance(
            self.metadef_property, _metadef_property.MetadefProperty
        )
        self.assertEqual(self.attrs['name'], self.metadef_property.name)
        self.assertEqual(self.attrs['title'], self.metadef_property.title)
        self.assertEqual(self.attrs['type'], self.metadef_property.type)
        self.assertEqual(
            self.attrs['description'], self.metadef_property.description
        )
        self.assertEqual(self.attrs['enum'], self.metadef_property.enum)

    def tearDown(self):
        # we do this in tearDown rather than via 'addCleanup' since we want to
        # wait for the deletion of the resource to ensure it completes
        self.operator_cloud.image.delete_metadef_property(
            self.metadef_property, self.metadef_namespace
        )
        self.operator_cloud.image.delete_metadef_namespace(
            self.metadef_namespace
        )
        self.operator_cloud.image.wait_for_delete(self.metadef_namespace)

        super().tearDown()

    def test_metadef_property(self):
        # get metadef property
        metadef_property = self.operator_cloud.image.get_metadef_property(
            self.metadef_property, self.metadef_namespace
        )
        self.assertIsNotNone(metadef_property)
        self.assertIsInstance(
            metadef_property, _metadef_property.MetadefProperty
        )
        self.assertEqual(self.attrs['name'], metadef_property.name)
        self.assertEqual(self.attrs['title'], metadef_property.title)
        self.assertEqual(self.attrs['type'], metadef_property.type)
        self.assertEqual(
            self.attrs['description'], metadef_property.description
        )
        self.assertEqual(self.attrs['enum'], metadef_property.enum)

        # (no find_metadef_property method)

        # list
        metadef_properties = list(
            self.operator_cloud.image.metadef_properties(
                self.metadef_namespace
            )
        )
        self.assertIsNotNone(metadef_properties)
        self.assertIsInstance(
            metadef_properties[0], _metadef_property.MetadefProperty
        )

        # update
        self.attrs['title'] = ''.join(
            random.choice(string.ascii_lowercase) for _ in range(10)
        )
        self.attrs['description'] = ''.join(
            random.choice(string.ascii_lowercase) for _ in range(10)
        )
        metadef_property = self.operator_cloud.image.update_metadef_property(
            self.metadef_property,
            self.metadef_namespace.namespace,
            **self.attrs,
        )
        self.assertIsNotNone(metadef_property)
        self.assertIsInstance(
            metadef_property,
            _metadef_property.MetadefProperty,
        )
        metadef_property = self.operator_cloud.image.get_metadef_property(
            self.metadef_property.name, self.metadef_namespace
        )
        self.assertEqual(
            self.attrs['title'],
            metadef_property.title,
        )
        self.assertEqual(
            self.attrs['description'],
            metadef_property.description,
        )
