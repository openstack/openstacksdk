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

from openstack.network.v2 import security_group
from openstack.network.v2 import security_group_rule
from openstack.tests.functional import base


class TestSecurityGroupRule(base.BaseFunctionalTest):

    NAME = uuid.uuid4().hex
    IPV4 = 'IPv4'
    PROTO = 'tcp'
    PORT = 22
    DIR = 'ingress'
    ID = None
    RULE_ID = None

    @classmethod
    def setUpClass(cls):
        super(TestSecurityGroupRule, cls).setUpClass()
        sot = cls.conn.network.create_security_group(name=cls.NAME)
        assert isinstance(sot, security_group.SecurityGroup)
        cls.assertIs(cls.NAME, sot.name)
        cls.ID = sot.id
        rul = cls.conn.network.create_security_group_rule(
            direction=cls.DIR, ethertype=cls.IPV4,
            port_range_max=cls.PORT, port_range_min=cls.PORT,
            protocol=cls.PROTO, security_group_id=cls.ID)
        assert isinstance(rul, security_group_rule.SecurityGroupRule)
        cls.assertIs(cls.ID, rul.security_group_id)
        cls.RULE_ID = rul.id

    @classmethod
    def tearDownClass(cls):
        sot = cls.conn.network.delete_security_group_rule(cls.RULE_ID,
                                                          ignore_missing=False)
        cls.assertIs(None, sot)
        sot = cls.conn.network.delete_security_group(cls.ID,
                                                     ignore_missing=False)
        cls.assertIs(None, sot)

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
