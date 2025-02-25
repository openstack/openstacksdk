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

from openstack.image.v2 import metadef_schema as _metadef_schema
from openstack.tests.functional.image.v2 import base


class TestMetadefSchema(base.BaseImageTest):
    def test_get_metadef_namespace_schema(self):
        metadef_schema = (
            self.operator_cloud.image.get_metadef_namespace_schema()
        )
        self.assertIsNotNone(metadef_schema)
        self.assertIsInstance(metadef_schema, _metadef_schema.MetadefSchema)

    def test_get_metadef_namespaces_schema(self):
        metadef_schema = (
            self.operator_cloud.image.get_metadef_namespaces_schema()
        )
        self.assertIsNotNone(metadef_schema)
        self.assertIsInstance(metadef_schema, _metadef_schema.MetadefSchema)

    def test_get_metadef_resource_type_schema(self):
        metadef_schema = (
            self.operator_cloud.image.get_metadef_resource_type_schema()
        )
        self.assertIsNotNone(metadef_schema)
        self.assertIsInstance(metadef_schema, _metadef_schema.MetadefSchema)

    def test_get_metadef_resource_types_schema(self):
        metadef_schema = (
            self.operator_cloud.image.get_metadef_resource_types_schema()
        )
        self.assertIsNotNone(metadef_schema)
        self.assertIsInstance(metadef_schema, _metadef_schema.MetadefSchema)

    def test_get_metadef_object_schema(self):
        metadef_schema = self.operator_cloud.image.get_metadef_object_schema()
        self.assertIsNotNone(metadef_schema)
        self.assertIsInstance(metadef_schema, _metadef_schema.MetadefSchema)

    def test_get_metadef_objects_schema(self):
        metadef_schema = self.operator_cloud.image.get_metadef_objects_schema()
        self.assertIsNotNone(metadef_schema)
        self.assertIsInstance(metadef_schema, _metadef_schema.MetadefSchema)

    def test_get_metadef_property_schema(self):
        metadef_schema = (
            self.operator_cloud.image.get_metadef_property_schema()
        )
        self.assertIsNotNone(metadef_schema)
        self.assertIsInstance(metadef_schema, _metadef_schema.MetadefSchema)

    def test_get_metadef_properties_schema(self):
        metadef_schema = (
            self.operator_cloud.image.get_metadef_properties_schema()
        )
        self.assertIsNotNone(metadef_schema)
        self.assertIsInstance(metadef_schema, _metadef_schema.MetadefSchema)

    def test_get_metadef_tag_schema(self):
        metadef_schema = self.operator_cloud.image.get_metadef_tag_schema()
        self.assertIsNotNone(metadef_schema)
        self.assertIsInstance(metadef_schema, _metadef_schema.MetadefSchema)

    def test_get_metadef_tags_schema(self):
        metadef_schema = self.operator_cloud.image.get_metadef_tags_schema()
        self.assertIsNotNone(metadef_schema)
        self.assertIsInstance(metadef_schema, _metadef_schema.MetadefSchema)
