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


from openstack.tests.functional import base


class TestExtension(base.BaseFunctionalTest):
    def test_list(self):
        extensions = list(self.user_cloud.network.extensions())
        self.assertGreater(len(extensions), 0)

        for ext in extensions:
            self.assertIsInstance(ext.name, str)
            self.assertIsInstance(ext.alias, str)

    def test_find(self):
        extension = self.user_cloud.network.find_extension("external-net")
        self.assertEqual("Neutron external network", extension.name)
