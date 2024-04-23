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


from openstack import resource
from openstack.shared_file_system.v2 import share_instance as _share_instance
from openstack.tests.functional.shared_file_system import base


class ShareInstanceTest(base.BaseSharedFileSystemTest):
    min_microversion = '2.7'

    def setUp(self):
        super().setUp()

        self.SHARE_NAME = self.getUniqueString()
        my_share = self.create_share(
            name=self.SHARE_NAME,
            size=2,
            share_type="dhss_false",
            share_protocol='NFS',
            description=None,
        )
        self.SHARE_ID = my_share.id
        instances_list = self.operator_cloud.share.share_instances()
        self.SHARE_INSTANCE_ID = None
        for i in instances_list:
            if i.share_id == self.SHARE_ID:
                self.SHARE_INSTANCE_ID = i.id

    def test_get(self):
        sot = self.operator_cloud.share.get_share_instance(
            self.SHARE_INSTANCE_ID
        )
        assert isinstance(sot, _share_instance.ShareInstance)
        self.assertEqual(self.SHARE_INSTANCE_ID, sot.id)

    def test_list_share_instances(self):
        share_instances = self.operator_cloud.share.share_instances()
        self.assertGreater(len(list(share_instances)), 0)
        for share_instance in share_instances:
            for attribute in (
                'id',
                'name',
                'created_at',
                'access_rules_status',
                'availability_zone',
            ):
                self.assertTrue(hasattr(share_instance, attribute))

    def test_reset(self):
        res = self.operator_cloud.share.reset_share_instance_status(
            self.SHARE_INSTANCE_ID, 'error'
        )
        self.assertIsNone(res)
        sot = self.operator_cloud.share.get_share_instance(
            self.SHARE_INSTANCE_ID
        )
        self.assertEqual('error', sot.status)

    def test_delete(self):
        sot = self.operator_cloud.share.get_share_instance(
            self.SHARE_INSTANCE_ID
        )
        fdel = self.operator_cloud.share.delete_share_instance(
            self.SHARE_INSTANCE_ID
        )
        resource.wait_for_delete(
            self.operator_cloud.share,
            sot,
            wait=self._wait_for_timeout,
            interval=2,
        )
        self.assertIsNone(fdel)
