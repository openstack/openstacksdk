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


from openstack.network.v2 import qos_policy as _qos_policy
from openstack.tests.functional import base


class TestQoSPolicy(base.BaseFunctionalTest):
    QOS_POLICY_ID = None
    IS_SHARED = False
    IS_DEFAULT = False
    RULES: list[str] = []
    QOS_POLICY_DESCRIPTION = "QoS policy description"

    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        # Skip the tests if qos extension is not enabled.
        if not self.operator_cloud.network.find_extension("qos"):
            self.skipTest("Network qos extension disabled")

        self.QOS_POLICY_NAME = self.getUniqueString()
        self.QOS_POLICY_NAME_UPDATED = self.getUniqueString()
        qos = self.operator_cloud.network.create_qos_policy(
            description=self.QOS_POLICY_DESCRIPTION,
            name=self.QOS_POLICY_NAME,
            shared=self.IS_SHARED,
            is_default=self.IS_DEFAULT,
        )
        assert isinstance(qos, _qos_policy.QoSPolicy)
        self.assertEqual(self.QOS_POLICY_NAME, qos.name)
        self.QOS_POLICY_ID = qos.id

    def tearDown(self):
        sot = self.operator_cloud.network.delete_qos_policy(self.QOS_POLICY_ID)
        self.assertIsNone(sot)
        super().tearDown()

    def test_find(self):
        sot = self.operator_cloud.network.find_qos_policy(self.QOS_POLICY_NAME)
        self.assertEqual(self.QOS_POLICY_ID, sot.id)

    def test_get(self):
        sot = self.operator_cloud.network.get_qos_policy(self.QOS_POLICY_ID)
        self.assertEqual(self.QOS_POLICY_NAME, sot.name)
        self.assertEqual(self.IS_SHARED, sot.is_shared)
        self.assertEqual(self.RULES, sot.rules)
        self.assertEqual(self.QOS_POLICY_DESCRIPTION, sot.description)
        self.assertEqual(self.IS_DEFAULT, sot.is_default)

    def test_list(self):
        names = [o.name for o in self.operator_cloud.network.qos_policies()]
        self.assertIn(self.QOS_POLICY_NAME, names)

    def test_update(self):
        sot = self.operator_cloud.network.update_qos_policy(
            self.QOS_POLICY_ID, name=self.QOS_POLICY_NAME_UPDATED
        )
        self.assertEqual(self.QOS_POLICY_NAME_UPDATED, sot.name)

    def test_set_tags(self):
        sot = self.operator_cloud.network.get_qos_policy(self.QOS_POLICY_ID)
        self.assertEqual([], sot.tags)

        self.operator_cloud.network.set_tags(sot, ["blue"])
        sot = self.operator_cloud.network.get_qos_policy(self.QOS_POLICY_ID)
        self.assertEqual(["blue"], sot.tags)

        self.operator_cloud.network.set_tags(sot, [])
        sot = self.operator_cloud.network.get_qos_policy(self.QOS_POLICY_ID)
        self.assertEqual([], sot.tags)
