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

from openstack.key_manager.v1 import project_quota
from openstack.tests.unit import base


EXAMPLE = {
    'secrets': 10,
    'orders': 20,
    'containers': -1,
    'consumers': 10,
    'cas': 5,
}


class TestProjectQuota(base.TestCase):
    def test_basic(self):
        sot = project_quota.ProjectQuota()
        self.assertEqual('project_quotas', sot.resource_key)
        self.assertEqual('project_quotas', sot.resources_key)
        self.assertEqual('/project-quotas', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = project_quota.ProjectQuota(**EXAMPLE)
        self.assertEqual(EXAMPLE['secrets'], sot.secrets)
        self.assertEqual(EXAMPLE['orders'], sot.orders)
        self.assertEqual(EXAMPLE['containers'], sot.containers)
        self.assertEqual(EXAMPLE['consumers'], sot.consumers)
        self.assertEqual(EXAMPLE['cas'], sot.cas)
