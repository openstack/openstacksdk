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
from openstack.tests.functional.image.v2 import base


class TestMetadefNamespace(base.BaseImageTest):
    # TODO(stephenfin): We should use setUpClass here for MOAR SPEED!!!
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

    def tearDown(self):
        # we do this in tearDown rather than via 'addCleanup' since we want to
        # wait for the deletion of the resource to ensure it completes
        self.operator_cloud.image.delete_metadef_namespace(
            self.metadef_namespace
        )
        self.operator_cloud.image.wait_for_delete(self.metadef_namespace)

        super().tearDown()

    def test_metadef_namespace(self):
        # get
        metadef_namespace = self.operator_cloud.image.get_metadef_namespace(
            self.metadef_namespace.namespace
        )
        self.assertEqual(
            self.metadef_namespace.namespace,
            metadef_namespace.namespace,
        )

        # (no find_metadef_namespace method)

        # list
        metadef_namespaces = list(
            self.operator_cloud.image.metadef_namespaces()
        )
        # there are a load of default metadef namespaces so we don't assert
        # that this is the *only* metadef namespace present
        self.assertIn(
            self.metadef_namespace.namespace,
            {n.namespace for n in metadef_namespaces},
        )

        # update
        # there's a limit on display name and description lengths and no
        # inherent need for randomness so we use fixed strings
        metadef_namespace_display_name = 'A display name'
        metadef_namespace_description = 'A description'
        metadef_namespace = self.operator_cloud.image.update_metadef_namespace(
            self.metadef_namespace,
            display_name=metadef_namespace_display_name,
            description=metadef_namespace_description,
        )
        self.assertIsInstance(
            metadef_namespace,
            _metadef_namespace.MetadefNamespace,
        )
        metadef_namespace = self.operator_cloud.image.get_metadef_namespace(
            self.metadef_namespace.namespace
        )
        self.assertEqual(
            metadef_namespace_display_name,
            metadef_namespace.display_name,
        )
        self.assertEqual(
            metadef_namespace_description,
            metadef_namespace.description,
        )
