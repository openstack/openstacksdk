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


from openstack.network.v2 import security_group
from openstack.network.v2 import security_group_rule
from openstack.tests.functional import base


class TestSecurityGroupRule(base.BaseFunctionalTest):

    IPV4 = 'IPv4'
    PROTO = 'tcp'
    PORT = 22
    DIR = 'ingress'
    ID = None
    RULE_ID = None

    def setUp(self):
        super(TestSecurityGroupRule, self).setUp()
        self.NAME = self.getUniqueString()
        sot = self.conn.network.create_security_group(name=self.NAME)
        assert isinstance(sot, security_group.SecurityGroup)
        self.assertEqual(self.NAME, sot.name)
        self.ID = sot.id
        rul = self.conn.network.create_security_group_rule(
            direction=self.DIR, ethertype=self.IPV4,
            port_range_max=self.PORT, port_range_min=self.PORT,
            protocol=self.PROTO, security_group_id=self.ID)
        assert isinstance(rul, security_group_rule.SecurityGroupRule)
        self.assertEqual(self.ID, rul.security_group_id)
        self.RULE_ID = rul.id

    def tearDown(self):
        sot = self.conn.network.delete_security_group_rule(
            self.RULE_ID, ignore_missing=False)
        self.assertIsNone(sot)
        sot = self.conn.network.delete_security_group(
            self.ID, ignore_missing=False)
        self.assertIsNone(sot)
        super(TestSecurityGroupRule, self).tearDown()

    def test_find(self):
        sot = self.conn.network.find_security_group_rule(self.RULE_ID)
        self.assertEqual(self.RULE_ID, sot.id)

    def test_get(self):
        sot = self.conn.network.get_security_group_rule(self.RULE_ID)
        self.assertEqual(self.RULE_ID, sot.id)
        self.assertEqual(self.DIR, sot.direction)
        self.assertEqual(self.PROTO, sot.protocol)
        self.assertEqual(self.PORT, sot.port_range_min)
        self.assertEqual(self.PORT, sot.port_range_max)
        self.assertEqual(self.ID, sot.security_group_id)

    def test_list(self):
        ids = [o.id for o in self.conn.network.security_group_rules()]
        self.assertIn(self.RULE_ID, ids)
