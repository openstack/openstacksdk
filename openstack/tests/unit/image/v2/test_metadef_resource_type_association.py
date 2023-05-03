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

from openstack.image.v2 import metadef_resource_type
from openstack.tests.unit import base


EXAMPLE = {
    "name": "OS::Cinder::Volume",
    "prefix": "CIM_PASD_",
    "properties_target": "image",
    "created_at": "2022-07-09T04:10:38Z",
}


class TestMetadefResourceTypeAssociation(base.TestCase):
    def test_basic(self):
        sot = metadef_resource_type.MetadefResourceTypeAssociation()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('resource_type_associations', sot.resources_key)
        self.assertEqual(
            '/metadefs/namespaces/%(namespace_name)s/resource_types',
            sot.base_path,
        )
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = metadef_resource_type.MetadefResourceTypeAssociation(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['prefix'], sot.prefix)
        self.assertEqual(EXAMPLE['properties_target'], sot.properties_target)
