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

from openstack.dns.v2 import blacklist as _blacklist
from openstack.tests.functional import base


class TestBlackList(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('dns')

        # Note: use a unique UUID pattern to avoid test collisions
        self.pattern = rf".*\.test-{uuid.uuid4().hex}.com"
        self.description = self.getUniqueString('blacklist')

    def _delete_blacklist(self, blacklist):
        ret = self.operator_cloud.dns.delete_blacklist(blacklist.id)
        self.assertIsNone(ret)

    def test_blacklist(self):
        # create blacklist
        blacklist = self.operator_cloud.dns.create_blacklist(
            pattern=self.pattern,
            description=self.description,
        )
        self.assertIsNotNone(blacklist.id)
        self.assertIsInstance(blacklist, _blacklist.Blacklist)
        self.assertEqual(self.pattern, blacklist.pattern)
        self.assertEqual(self.description, blacklist.description)
        self.addCleanup(self._delete_blacklist, blacklist)

        # update blacklist
        blacklist = self.operator_cloud.dns.update_blacklist(
            blacklist, pattern=self.pattern, description=self.description
        )
        self.assertIsInstance(blacklist, _blacklist.Blacklist)
        self.assertEqual(self.pattern, blacklist.pattern)
        self.assertEqual(self.description, blacklist.description)

        # get blacklist
        blacklist = self.operator_cloud.dns.get_blacklist(blacklist.id)
        self.assertIsInstance(blacklist, _blacklist.Blacklist)
        self.assertEqual(self.pattern, blacklist.pattern)
        self.assertEqual(self.description, blacklist.description)

        # list all blacklists
        blacklists = list(self.operator_cloud.dns.blacklists())
        self.assertIsInstance(blacklists[0], _blacklist.Blacklist)
        self.assertIn(self.pattern, {x.pattern for x in blacklists})
        self.operator_cloud.dns.delete_blacklist(blacklist.id)
