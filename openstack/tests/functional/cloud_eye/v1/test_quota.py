#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from openstack.tests.functional import base


class TestQuota(base.BaseFunctionalTest):
    @classmethod
    def setUpClass(cls):
        super(TestQuota, cls).setUpClass()

    def test_list_quotas(self):
        quotas = list(self.conn.cloud_eye.quotas())
        self.assertTrue(len(quotas) > 0)
