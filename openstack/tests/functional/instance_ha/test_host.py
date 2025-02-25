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


from openstack.compute.v2 import hypervisor
from openstack import connection
from openstack.tests.functional import base

HYPERVISORS: list[hypervisor.Hypervisor] = []


def hypervisors():
    global HYPERVISORS
    if HYPERVISORS:
        return True
    HYPERVISORS = connection.Connection.list_hypervisors(
        connection.from_config(cloud_name=base.TEST_CLOUD_NAME)
    )
    return bool(HYPERVISORS)


class TestHost(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('instance-ha')
        self.NAME = self.getUniqueString()

        if not hypervisors():
            self.skipTest(
                "Skip TestHost as there are no hypervisors configured in nova"
            )

        # Create segment
        self.segment = self.operator_cloud.ha.create_segment(
            name=self.NAME, recovery_method='auto', service_type='COMPUTE'
        )

        # Create valid host
        self.NAME = HYPERVISORS[0].name
        self.host = self.operator_cloud.ha.create_host(
            segment_id=self.segment.uuid,
            name=self.NAME,
            type='COMPUTE',
            control_attributes='SSH',
        )

        # Delete host
        self.addCleanup(
            self.operator_cloud.ha.delete_host,
            self.segment.uuid,
            self.host.uuid,
        )
        # Delete segment
        self.addCleanup(
            self.operator_cloud.ha.delete_segment, self.segment.uuid
        )

    def test_list(self):
        names = [
            o.name
            for o in self.operator_cloud.ha.hosts(
                self.segment.uuid,
                failover_segment_id=self.segment.uuid,
                type='COMPUTE',
            )
        ]
        self.assertIn(self.NAME, names)

    def test_update(self):
        updated_host = self.operator_cloud.ha.update_host(
            self.host['uuid'],
            segment_id=self.segment.uuid,
            on_maintenance='True',
        )
        get_host = self.operator_cloud.ha.get_host(
            updated_host.uuid, updated_host.segment_id
        )
        self.assertEqual(True, get_host.on_maintenance)
