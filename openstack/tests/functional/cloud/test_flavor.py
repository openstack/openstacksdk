# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test_flavor
----------------------------------

Functional tests for `shade` flavor resource.
"""

from openstack.cloud.exc import OpenStackCloudException
from openstack.tests.functional.cloud import base


class TestFlavor(base.BaseFunctionalTestCase):

    def setUp(self):
        super(TestFlavor, self).setUp()

        # Generate a random name for flavors in this test
        self.new_item_name = self.getUniqueString('flavor')

        self.addCleanup(self._cleanup_flavors)

    def _cleanup_flavors(self):
        exception_list = list()
        for f in self.operator_cloud.list_flavors(get_extra=False):
            if f['name'].startswith(self.new_item_name):
                try:
                    self.operator_cloud.delete_flavor(f['id'])
                except Exception as e:
                    # We were unable to delete a flavor, let's try with next
                    exception_list.append(str(e))
                    continue
        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise OpenStackCloudException('\n'.join(exception_list))

    def test_create_flavor(self):
        flavor_name = self.new_item_name + '_create'
        flavor_kwargs = dict(
            name=flavor_name, ram=1024, vcpus=2, disk=10, ephemeral=5,
            swap=100, rxtx_factor=1.5, is_public=True
        )

        flavor = self.operator_cloud.create_flavor(**flavor_kwargs)

        self.assertIsNotNone(flavor['id'])

        # When properly normalized, we should always get an extra_specs
        # and expect empty dict on create.
        self.assertIn('extra_specs', flavor)
        self.assertEqual({}, flavor['extra_specs'])

        # We should also always have ephemeral and public attributes
        self.assertIn('ephemeral', flavor)
        self.assertIn('OS-FLV-EXT-DATA:ephemeral', flavor)
        self.assertEqual(5, flavor['ephemeral'])
        self.assertIn('is_public', flavor)
        self.assertIn('os-flavor-access:is_public', flavor)
        self.assertTrue(flavor['is_public'])

        for key in flavor_kwargs.keys():
            self.assertIn(key, flavor)
        for key, value in flavor_kwargs.items():
            self.assertEqual(value, flavor[key])

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
        self.operator_cloud.create_flavor(**public_kwargs)
        self.operator_cloud.create_flavor(**private_kwargs)

        flavors = self.operator_cloud.list_flavors(get_extra=False)

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
        priv_flavor_name = self.new_item_name + '_private'
        private_kwargs = dict(
            name=priv_flavor_name, ram=1024, vcpus=2, disk=10, is_public=False
        )
        new_flavor = self.operator_cloud.create_flavor(**private_kwargs)

        # Validate the 'demo' user cannot see the new flavor
        flavors = self.user_cloud.search_flavors(priv_flavor_name)
        self.assertEqual(0, len(flavors))

        # We need the tenant ID for the 'demo' user
        project = self.operator_cloud.get_project('demo')
        self.assertIsNotNone(project)

        # Now give 'demo' access
        self.operator_cloud.add_flavor_access(new_flavor['id'], project['id'])

        # Now see if the 'demo' user has access to it
        flavors = self.user_cloud.search_flavors(priv_flavor_name)
        self.assertEqual(1, len(flavors))
        self.assertEqual(priv_flavor_name, flavors[0]['name'])

        # Now see if the 'demo' user has access to it without needing
        #  the demo_cloud access.
        acls = self.operator_cloud.list_flavor_access(new_flavor['id'])
        self.assertEqual(1, len(acls))
        self.assertEqual(project['id'], acls[0]['project_id'])

        # Now revoke the access and make sure we can't find it
        self.operator_cloud.remove_flavor_access(new_flavor['id'],
                                                 project['id'])
        flavors = self.user_cloud.search_flavors(priv_flavor_name)
        self.assertEqual(0, len(flavors))

    def test_set_unset_flavor_specs(self):
        """
        Test setting and unsetting flavor extra specs
        """
        flavor_name = self.new_item_name + '_spec_test'
        kwargs = dict(
            name=flavor_name, ram=1024, vcpus=2, disk=10
        )
        new_flavor = self.operator_cloud.create_flavor(**kwargs)

        # Expect no extra_specs
        self.assertEqual({}, new_flavor['extra_specs'])

        # Now set them
        extra_specs = {'foo': 'aaa', 'bar': 'bbb'}
        self.operator_cloud.set_flavor_specs(new_flavor['id'], extra_specs)
        mod_flavor = self.operator_cloud.get_flavor(
            new_flavor['id'], get_extra=True)

        # Verify extra_specs were set
        self.assertIn('extra_specs', mod_flavor)
        self.assertEqual(extra_specs, mod_flavor['extra_specs'])

        # Unset the 'foo' value
        self.operator_cloud.unset_flavor_specs(mod_flavor['id'], ['foo'])
        mod_flavor = self.operator_cloud.get_flavor_by_id(
            new_flavor['id'], get_extra=True)

        # Verify 'foo' is unset and 'bar' is still set
        self.assertEqual({'bar': 'bbb'}, mod_flavor['extra_specs'])
