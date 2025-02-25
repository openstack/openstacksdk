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

from openstack.image.v2 import schema as _schema
from openstack.tests.functional.image.v2 import base


class TestSchema(base.BaseImageTest):
    def test_get_images_schema(self):
        schema = self.operator_cloud.image.get_images_schema()
        self.assertIsNotNone(schema)
        self.assertIsInstance(schema, _schema.Schema)

    def test_get_image_schema(self):
        schema = self.operator_cloud.image.get_image_schema()
        self.assertIsNotNone(schema)
        self.assertIsInstance(schema, _schema.Schema)

    def test_get_members_schema(self):
        schema = self.operator_cloud.image.get_members_schema()
        self.assertIsNotNone(schema)
        self.assertIsInstance(schema, _schema.Schema)

    def test_get_member_schema(self):
        schema = self.operator_cloud.image.get_member_schema()
        self.assertIsNotNone(schema)
        self.assertIsInstance(schema, _schema.Schema)
