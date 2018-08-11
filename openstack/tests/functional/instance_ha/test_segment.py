# Copyright (C) 2018 NTT DATA
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from openstack.tests.functional import base


class TestSegment(base.BaseFunctionalTest):

    def setUp(self):
        super(TestSegment, self).setUp()
        self.require_service('instance-ha')
        self.NAME = self.getUniqueString()

        # Create segment
        self.segment = self.conn.ha.create_segment(
            name=self.NAME, recovery_method='auto',
            service_type='COMPUTE')

        # Delete segment
        self.addCleanup(self.conn.ha.delete_segment, self.segment['uuid'])

    def test_list(self):
        names = [o.name for o in self.conn.ha.segments(
            recovery_method='auto')]
        self.assertIn(self.NAME, names)

    def test_update(self):
        updated_segment = self.conn.ha.update_segment(self.segment['uuid'],
                                                      name='UPDATED-NAME')
        get_updated_segment = self.conn.ha.get_segment(updated_segment.uuid)
        self.assertEqual('UPDATED-NAME', get_updated_segment.name)
