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
    RULES = []
    QOS_POLICY_DESCRIPTION = "QoS policy description"

    def setUp(self):
        super(TestQoSPolicy, self).setUp()
        self.QOS_POLICY_NAME = self.getUniqueString()
        self.QOS_POLICY_NAME_UPDATED = self.getUniqueString()
        qos = self.conn.network.create_qos_policy(
            description=self.QOS_POLICY_DESCRIPTION,
            name=self.QOS_POLICY_NAME,
            shared=self.IS_SHARED,
            is_default=self.IS_DEFAULT,
        )
        assert isinstance(qos, _qos_policy.QoSPolicy)
        self.assertEqual(self.QOS_POLICY_NAME, qos.name)
        self.QOS_POLICY_ID = qos.id

    def tearDown(self):
        sot = self.conn.network.delete_qos_policy(self.QOS_POLICY_ID)
        self.assertIsNone(sot)
        super(TestQoSPolicy, self).tearDown()

    def test_find(self):
        sot = self.conn.network.find_qos_policy(self.QOS_POLICY_NAME)
        self.assertEqual(self.QOS_POLICY_ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_qos_policy(self.QOS_POLICY_ID)
        self.assertEqual(self.QOS_POLICY_NAME, sot.name)
        self.assertEqual(self.IS_SHARED, sot.is_shared)
        self.assertEqual(self.RULES, sot.rules)
        self.assertEqual(self.QOS_POLICY_DESCRIPTION, sot.description)
        self.assertEqual(self.IS_DEFAULT, sot.is_default)

    def test_list(self):
        names = [o.name for o in self.conn.network.qos_policies()]
        self.assertIn(self.QOS_POLICY_NAME, names)

    def test_update(self):
        sot = self.conn.network.update_qos_policy(
            self.QOS_POLICY_ID,
            name=self.QOS_POLICY_NAME_UPDATED)
        self.assertEqual(self.QOS_POLICY_NAME_UPDATED, sot.name)

    def test_set_tags(self):
        sot = self.conn.network.get_qos_policy(self.QOS_POLICY_ID)
        self.assertEqual([], sot.tags)

        self.conn.network.set_tags(sot, ['blue'])
        sot = self.conn.network.get_qos_policy(self.QOS_POLICY_ID)
        self.assertEqual(['blue'], sot.tags)

        self.conn.network.set_tags(sot, [])
        sot = self.conn.network.get_qos_policy(self.QOS_POLICY_ID)
        self.assertEqual([], sot.tags)
