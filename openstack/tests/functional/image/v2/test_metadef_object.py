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

from openstack.image.v2 import metadef_namespace as _metadef_namespace
from openstack.image.v2 import metadef_object as _metadef_object
from openstack.tests.functional.image.v2 import base


class TestMetadefObject(base.BaseImageTest):
    def setUp(self):
        super().setUp()

        # create namespace for object
        namespace = self.getUniqueString().split('.')[-1]
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

        # create object
        object = self.getUniqueString().split('.')[-1]
        self.metadef_object = self.operator_cloud.image.create_metadef_object(
            name=object,
            namespace=self.metadef_namespace,
        )
        self.assertIsInstance(
            self.metadef_object,
            _metadef_object.MetadefObject,
        )
        self.assertEqual(object, self.metadef_object.name)

    def tearDown(self):
        self.operator_cloud.image.delete_metadef_object(
            self.metadef_object,
            self.metadef_object.namespace_name,
        )
        self.operator_cloud.image.wait_for_delete(self.metadef_object)

        self.operator_cloud.image.delete_metadef_namespace(
            self.metadef_namespace
        )
        self.operator_cloud.image.wait_for_delete(self.metadef_namespace)

        super().tearDown()

    def test_metadef_objects(self):
        # get
        metadef_object = self.operator_cloud.image.get_metadef_object(
            self.metadef_object.name,
            self.metadef_namespace,
        )
        self.assertEqual(
            self.metadef_object.namespace_name,
            metadef_object.namespace_name,
        )
        self.assertEqual(
            self.metadef_object.name,
            metadef_object.name,
        )

        # list
        metadef_objects = list(
            self.operator_cloud.image.metadef_objects(
                self.metadef_object.namespace_name
            )
        )
        # there are a load of default metadef objects so we don't assert
        # that this is the *only* metadef objects present
        self.assertIn(
            self.metadef_object.name,
            {o.name for o in metadef_objects},
        )

        # update
        metadef_object_new_name = 'New object name'
        metadef_object_new_description = 'New object description'
        metadef_object = self.operator_cloud.image.update_metadef_object(
            self.metadef_object.name,
            namespace=self.metadef_object.namespace_name,
            name=metadef_object_new_name,
            description=metadef_object_new_description,
        )
        self.assertIsInstance(
            metadef_object,
            _metadef_object.MetadefObject,
        )
        self.assertEqual(
            metadef_object_new_name,
            metadef_object.name,
        )
        self.assertEqual(
            metadef_object_new_description,
            metadef_object.description,
        )
