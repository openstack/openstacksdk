# -*- coding: utf-8 -*-

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

"""
test_usage
----------------------------------

Functional tests for `shade` usage method
"""
import datetime

from shade.tests.functional import base


class TestUsage(base.BaseFunctionalTestCase):

    def test_get_compute_usage(self):
        '''Test usage functionality'''
        start = datetime.datetime.now() - datetime.timedelta(seconds=5)
        usage = self.operator_cloud.get_compute_usage('demo', start)
        self.add_info_on_exception('usage', usage)
        self.assertIsNotNone(usage)
        self.assertIn('total_hours', usage)
        self.assertIn('started_at', usage)
        self.assertEqual(start.isoformat(), usage['started_at'])
        self.assertIn('location', usage)
