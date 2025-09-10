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

from openstack.dns.v2 import tld as _tld
from openstack.tests.functional import base


class TestTLD(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()

        self.require_service('dns')

        self.tld_name = 'xyz'
        self.tld_description = 'The xyz TLD'

    def test_tld(self):
        # create the tld

        tld = self.operator_cloud.dns.create_tld(
            name=self.tld_name, description=self.tld_description
        )
        self.assertIsInstance(tld, _tld.TLD)
        self.assertEqual(self.tld_description, tld.description)
        self.addCleanup(self.operator_cloud.dns.delete_tld, tld)

        # update the tld

        tld = self.operator_cloud.dns.update_tld(
            tld, description=self.tld_description
        )
        self.assertIsInstance(tld, _tld.TLD)
        self.assertEqual(self.tld_description, tld.description)

        # retrieve details of the (updated) tld by ID

        tld = self.operator_cloud.dns.get_tld(tld.id)
        self.assertIsInstance(tld, _tld.TLD)
        self.assertEqual(self.tld_description, tld.description)

        # retrieve details of the (updated) tld by name

        tld = self.operator_cloud.dns.find_tld(tld.name)
        self.assertIsInstance(tld, _tld.TLD)
        self.assertEqual(self.tld_description, tld.description)

        # list all tlds
        tlds = list(self.operator_cloud.dns.tlds())
        self.assertIsInstance(tlds[0], _tld.TLD)
        self.assertIn(
            self.tld_name, {x.name for x in self.operator_cloud.dns.tlds()}
        )
