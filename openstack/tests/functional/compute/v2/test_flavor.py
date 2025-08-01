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

from openstack.compute.v2 import flavor as _flavor
from openstack.tests.functional import base


class TestFlavor(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        self.public_flavor_name = uuid.uuid4().hex
        self.private_flavor_name = uuid.uuid4().hex

    def _delete_flavor(self, flavor):
        ret = self.operator_cloud.compute.delete_flavor(flavor)
        self.assertIsNone(ret)

    def test_flavor(self):
        # create flavors
        #
        # create a public and private flavor so we can test that they are both
        # listed for an operator

        public_flavor = self.operator_cloud.compute.create_flavor(
            name=self.public_flavor_name,
            ram=1024,
            vcpus=2,
            disk=10,
            is_public=True,
        )
        self.addCleanup(self._delete_flavor, public_flavor)
        self.assertIsInstance(public_flavor, _flavor.Flavor)

        private_flavor = self.operator_cloud.compute.create_flavor(
            name=self.private_flavor_name,
            ram=1024,
            vcpus=2,
            disk=10,
            is_public=False,
        )
        self.addCleanup(self._delete_flavor, private_flavor)
        self.assertIsInstance(private_flavor, _flavor.Flavor)

        # list all flavors
        #
        # flavor list will include the standard devstack flavors. We just want
        # to make sure both of the flavors we just created are present.
        flavors = list(self.operator_cloud.compute.flavors())
        self.assertIn(self.public_flavor_name, {x.name for x in flavors})
        self.assertIn(self.private_flavor_name, {x.name for x in flavors})

        # get flavor by ID

        flavor = self.operator_cloud.compute.get_flavor(public_flavor.id)
        self.assertEqual(flavor.id, public_flavor.id)

        # find flavor by name

        flavor = self.operator_cloud.compute.find_flavor(public_flavor.name)
        self.assertEqual(flavor.name, public_flavor.name)

        # update a flavor

        self.operator_cloud.compute.update_flavor(
            public_flavor,
            description="updated description",
        )

        # fetch the updated flavor

        flavor = self.operator_cloud.compute.get_flavor(public_flavor.id)
        self.assertEqual(flavor.description, "updated description")

    def test_flavor_access(self):
        # create private flavor

        flavor_name = uuid.uuid4().hex
        flavor = self.operator_cloud.compute.create_flavor(
            name=flavor_name, ram=128, vcpus=1, disk=0, is_public=False
        )
        self.addCleanup(self._delete_flavor, flavor)
        self.assertIsInstance(flavor, _flavor.Flavor)

        # validate the 'demo' user cannot see the new flavor

        flavor = self.user_cloud.compute.find_flavor(
            flavor_name, ignore_missing=True
        )
        self.assertIsNone(flavor)

        # validate we can see the new flavor ourselves

        flavor = self.operator_cloud.compute.find_flavor(
            flavor_name, ignore_missing=True
        )
        self.assertIsNotNone(flavor)
        self.assertEqual(flavor_name, flavor.name)

        # get demo project for access control

        project = self.operator_cloud.get_project('demo')
        self.assertIsNotNone(project)

        # give 'demo' access to the flavor

        self.operator_cloud.compute.flavor_add_tenant_access(
            flavor.id, project['id']
        )

        # verify that the 'demo' user now has access to it

        flavor = self.user_cloud.compute.find_flavor(
            flavor_name, ignore_missing=True
        )
        self.assertIsNotNone(flavor)

        # remove 'demo' access and check we can't find it anymore

        self.operator_cloud.compute.flavor_remove_tenant_access(
            flavor.id, project['id']
        )

        flavor = self.user_cloud.compute.find_flavor(
            flavor_name, ignore_missing=True
        )
        self.assertIsNone(flavor)

    def test_flavor_extra_specs(self):
        # create private flavor

        flavor_name = uuid.uuid4().hex
        flavor = self.operator_cloud.compute.create_flavor(
            is_public=False, name=flavor_name, ram=128, vcpus=1, disk=0
        )
        self.addCleanup(self._delete_flavor, flavor)
        self.assertIsInstance(flavor, _flavor.Flavor)

        # create extra_specs

        specs = {'a': 'b'}
        self.operator_cloud.compute.create_flavor_extra_specs(
            flavor, extra_specs=specs
        )

        # verify specs were created correctly

        flavor_with_specs = (
            self.operator_cloud.compute.fetch_flavor_extra_specs(flavor)
        )
        self.assertDictEqual(specs, flavor_with_specs.extra_specs)

        # update/add a single extra spec property

        self.operator_cloud.compute.update_flavor_extra_specs_property(
            flavor, 'c', 'd'
        )

        # fetch single property value

        prop_value = (
            self.operator_cloud.compute.get_flavor_extra_specs_property(
                flavor, 'c'
            )
        )
        self.assertEqual('d', prop_value)

        # delete the new property

        self.operator_cloud.compute.delete_flavor_extra_specs_property(
            flavor, 'c'
        )

        # re-fetch and ensure we're back to the previous state

        flavor_with_specs = (
            self.operator_cloud.compute.fetch_flavor_extra_specs(flavor)
        )
        self.assertDictEqual(specs, flavor_with_specs.extra_specs)
