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
import uuid

from openstack import exceptions
from openstack.tests.functional import base


class TestFlavor(base.BaseFunctionalTest):

    def setUp(self):
        super(TestFlavor, self).setUp()
        self.new_item_name = self.getUniqueString('flavor')
        self.one_flavor = list(self.conn.compute.flavors())[0]

    def test_flavors(self):
        flavors = list(self.conn.compute.flavors())
        self.assertGreater(len(flavors), 0)

        for flavor in flavors:
            self.assertIsInstance(flavor.id, str)
            self.assertIsInstance(flavor.name, str)
            self.assertIsInstance(flavor.disk, int)
            self.assertIsInstance(flavor.ram, int)
            self.assertIsInstance(flavor.vcpus, int)

    def test_find_flavors_by_id(self):
        rslt = self.conn.compute.find_flavor(self.one_flavor.id)
        self.assertEqual(rslt.id, self.one_flavor.id)

    def test_find_flavors_by_name(self):
        rslt = self.conn.compute.find_flavor(self.one_flavor.name)
        self.assertEqual(rslt.name, self.one_flavor.name)

    def test_find_flavors_no_match_ignore_true(self):
        rslt = self.conn.compute.find_flavor("not a flavor",
                                             ignore_missing=True)
        self.assertIsNone(rslt)

    def test_find_flavors_no_match_ignore_false(self):
        self.assertRaises(exceptions.ResourceNotFound,
                          self.conn.compute.find_flavor,
                          "not a flavor", ignore_missing=False)

    def test_list_flavors(self):
        pub_flavor_name = self.new_item_name + '_public'
        priv_flavor_name = self.new_item_name + '_private'
        public_kwargs = dict(
            name=pub_flavor_name, ram=1024, vcpus=2, disk=10, is_public=True
        )
        private_kwargs = dict(
            name=priv_flavor_name, ram=1024, vcpus=2, disk=10, is_public=False
        )

        # Create a public and private flavor. We expect both to be listed
        # for an operator.
        self.operator_cloud.compute.create_flavor(**public_kwargs)
        self.operator_cloud.compute.create_flavor(**private_kwargs)

        flavors = self.operator_cloud.compute.flavors()

        # Flavor list will include the standard devstack flavors. We just want
        # to make sure both of the flavors we just created are present.
        found = []
        for f in flavors:
            # extra_specs should be added within list_flavors()
            self.assertIn('extra_specs', f)
            if f['name'] in (pub_flavor_name, priv_flavor_name):
                found.append(f)
        self.assertEqual(2, len(found))

    def test_flavor_access(self):
        flavor_name = uuid.uuid4().hex
        flv = self.operator_cloud.compute.create_flavor(
            is_public=False,
            name=flavor_name,
            ram=128,
            vcpus=1,
            disk=0)
        self.addCleanup(self.conn.compute.delete_flavor, flv.id)
        # Validate the 'demo' user cannot see the new flavor
        flv_cmp = self.user_cloud.compute.find_flavor(flavor_name)
        self.assertIsNone(flv_cmp)

        # Validate we can see the new flavor ourselves
        flv_cmp = self.operator_cloud.compute.find_flavor(flavor_name)
        self.assertIsNotNone(flv_cmp)
        self.assertEqual(flavor_name, flv_cmp.name)

        project = self.operator_cloud.get_project('demo')
        self.assertIsNotNone(project)

        # Now give 'demo' access
        self.operator_cloud.compute.flavor_add_tenant_access(
            flv.id, project['id'])

        # Now see if the 'demo' user has access to it
        flv_cmp = self.user_cloud.compute.find_flavor(
            flavor_name)
        self.assertIsNotNone(flv_cmp)

        # Now remove 'demo' access and check we can't find it
        self.operator_cloud.compute.flavor_remove_tenant_access(
            flv.id, project['id'])

        flv_cmp = self.user_cloud.compute.find_flavor(
            flavor_name)
        self.assertIsNone(flv_cmp)

    def test_extra_props_calls(self):
        flavor_name = uuid.uuid4().hex
        flv = self.conn.compute.create_flavor(
            is_public=False,
            name=flavor_name,
            ram=128,
            vcpus=1,
            disk=0)
        self.addCleanup(self.conn.compute.delete_flavor, flv.id)
        # Create extra_specs
        specs = {
            'a': 'b'
        }
        self.conn.compute.create_flavor_extra_specs(flv, extra_specs=specs)
        # verify specs
        flv_cmp = self.conn.compute.fetch_flavor_extra_specs(flv)
        self.assertDictEqual(specs, flv_cmp.extra_specs)
        # update
        self.conn.compute.update_flavor_extra_specs_property(flv, 'c', 'd')
        val_cmp = self.conn.compute.get_flavor_extra_specs_property(flv, 'c')
        # fetch single prop
        self.assertEqual('d', val_cmp)
        # drop new prop
        self.conn.compute.delete_flavor_extra_specs_property(flv, 'c')
        # re-fetch and ensure prev state
        flv_cmp = self.conn.compute.fetch_flavor_extra_specs(flv)
        self.assertDictEqual(specs, flv_cmp.extra_specs)
