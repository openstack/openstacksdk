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

from unittest import mock

from openstack import exceptions
from openstack.tests.functional import base


# NOTE: method to make mypy happy.
def _get_command(*args):
    return mock.Mock()


class TestTagNeutron(base.BaseFunctionalTest):
    get_command = _get_command

    def test_set_tags(self):
        sot = self.get_command(self.ID)
        self.assertEqual([], sot.tags)

        self.user_cloud.network.set_tags(sot, ["blue"])
        sot = self.get_command(self.ID)
        self.assertEqual(["blue"], sot.tags)

        self.user_cloud.network.set_tags(sot, [])
        sot = self.get_command(self.ID)
        self.assertEqual([], sot.tags)

    def test_get_tags(self):
        sot = self.get_command(self.ID)
        self.assertEqual([], sot.tags)

        self.user_cloud.network.set_tags(sot, ["blue", "red"])
        tags = self.user_cloud.network.get_tags(sot)
        self.assertEqual(["blue", "red"], tags)

    def test_add_tag(self):
        sot = self.get_command(self.ID)
        self.assertEqual([], sot.tags)

        self.user_cloud.network.add_tag(sot, "blue")
        tags = self.user_cloud.network.get_tags(sot)
        self.assertEqual(["blue"], tags)

        # The operation is idempotent.
        self.user_cloud.network.add_tag(sot, "blue")
        tags = self.user_cloud.network.get_tags(sot)
        self.assertEqual(["blue"], tags)

    def test_remove_tag(self):
        sot = self.get_command(self.ID)
        self.assertEqual([], sot.tags)

        self.user_cloud.network.set_tags(sot, ["blue"])
        tags = self.user_cloud.network.get_tags(sot)
        self.assertEqual(["blue"], tags)

        self.user_cloud.network.remove_tag(sot, "blue")
        tags = self.user_cloud.network.get_tags(sot)
        self.assertEqual([], tags)

        # The operation is not idempotent.
        self.assertRaises(
            exceptions.NotFoundException,
            self.user_cloud.network.remove_tag,
            sot,
            "blue",
        )

    def test_remove_all_tags(self):
        sot = self.get_command(self.ID)
        self.assertEqual([], sot.tags)

        self.user_cloud.network.set_tags(sot, ["blue", "red"])
        sot = self.get_command(self.ID)
        self.assertEqual(["blue", "red"], sot.tags)

        self.user_cloud.network.remove_all_tags(sot)
        sot = self.get_command(self.ID)
        self.assertEqual([], sot.tags)

    def test_add_tags(self):
        # Skip the test if tag-creation extension is not enabled.
        if not self.user_cloud.network.find_extension("tag-creation"):
            self.skipTest("Network tag-creation extension disabled")

        sot = self.get_command(self.ID)
        self.assertEqual([], sot.tags)

        self.user_cloud.network.add_tags(sot, ["red", "green"])
        self.user_cloud.network.add_tags(sot, ["blue", "yellow"])
        sot = self.get_command(self.ID)
        self.assertEqual(["blue", "green", "red", "yellow"], sot.tags)

        # The operation is idempotent.
        self.user_cloud.network.add_tags(sot, ["blue", "yellow"])
        sot = self.get_command(self.ID)
        self.assertEqual(["blue", "green", "red", "yellow"], sot.tags)

        self.user_cloud.network.add_tags(sot, [])
        sot = self.get_command(self.ID)
        self.assertEqual(["blue", "green", "red", "yellow"], sot.tags)
