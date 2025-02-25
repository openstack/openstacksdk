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
from openstack.image.v2 import metadef_resource_type as _metadef_resource_type
from openstack.tests.functional.image.v2 import base


class TestMetadefResourceType(base.BaseImageTest):
    def setUp(self):
        super().setUp()

        # there's a limit on namespace length
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

        resource_type_name = 'test-resource-type'
        resource_type = {'name': resource_type_name}
        self.metadef_resource_type = (
            self.operator_cloud.image.create_metadef_resource_type_association(
                metadef_namespace=namespace, **resource_type
            )
        )
        self.assertIsInstance(
            self.metadef_resource_type,
            _metadef_resource_type.MetadefResourceTypeAssociation,
        )
        self.assertEqual(resource_type_name, self.metadef_resource_type.name)

    def tearDown(self):
        # we do this in tearDown rather than via 'addCleanup' since we want to
        # wait for the deletion of the resource to ensure it completes
        self.operator_cloud.image.delete_metadef_namespace(
            self.metadef_namespace
        )
        self.operator_cloud.image.wait_for_delete(self.metadef_namespace)

        super().tearDown()

    def test_metadef_resource_types(self):
        # list resource type associations
        associations = list(
            self.operator_cloud.image.metadef_resource_type_associations(
                metadef_namespace=self.metadef_namespace
            )
        )

        self.assertIn(
            self.metadef_resource_type.name, {a.name for a in associations}
        )

        # (no find_metadef_resource_type_association method)

        # list resource types
        resource_types = list(
            self.operator_cloud.image.metadef_resource_types()
        )

        self.assertIn(
            self.metadef_resource_type.name, {t.name for t in resource_types}
        )

        # delete
        self.operator_cloud.image.delete_metadef_resource_type_association(
            self.metadef_resource_type,
            metadef_namespace=self.metadef_namespace,
        )
