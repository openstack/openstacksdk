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

from openstack.shared_file_system.v2 import share_replica as _share_replica
from openstack.tests.functional.shared_file_system.v2 import base


class ShareReplicaTest(base.BaseSharedFileSystemTest):
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
        self.user_cloud.shared_file_system.wait_for_status(
            my_share,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        self.SHARE = my_share
        self.SHARE_ID = my_share.id
        srt = self.user_cloud.shared_file_system.create_share_replica(
            my_share.id
        )
        self.SHARE_REPLICA = srt
        self.user_cloud.shared_file_system.wait_for_status(
            self.SHARE_REPLICA,
            status='in_sync',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
            attribute='replica_state',
        )
        self.assertIsNotNone(srt)
        self.assertIsNotNone(srt.id)
        self.SHARE_REPLICA_ID = srt.id

    def tearDown(self):
        share_replicas = self.user_cloud.share.share_replicas()
        for share_replica in share_replicas:
            replica_state = getattr(share_replica, 'replica_state')
            if replica_state != 'active':
                self.user_cloud.shared_file_system.delete_share_replica(
                    share_replica, ignore_missing=True
                )
                self.user_cloud.shared_file_system.wait_for_delete(
                    share_replica, interval=2, wait=self._wait_for_timeout
                )
        sot = self.user_cloud.shared_file_system.delete_share(
            self.SHARE_ID, ignore_missing=True
        )
        self.user_cloud.shared_file_system.wait_for_delete(
            self.SHARE, interval=2, wait=self._wait_for_timeout
        )
        self.assertIsNone(sot)
        super().tearDown()

    def test_get(self):
        sot = self.user_cloud.shared_file_system.get_share_replica(
            self.SHARE_REPLICA_ID
        )
        assert isinstance(sot, _share_replica.ShareReplica)
        self.assertEqual(self.SHARE_REPLICA_ID, sot.id)

    def test_list_share_replicas(self):
        share_replicas = self.user_cloud.share.share_replicas()
        self.assertGreater(len(list(share_replicas)), 0)
        for share_replica in share_replicas:
            for attribute in ('id', 'name', 'created_at', 'replica_state'):
                self.assertTrue(hasattr(share_replica, attribute))

    def test_reset(self):
        res = self.operator_cloud.share.reset_share_replica_status(
            self.SHARE_REPLICA_ID, 'error'
        )
        self.assertIsNone(res)
        sot = self.user_cloud.share.get_share_replica(self.SHARE_REPLICA_ID)
        self.assertEqual('error', sot.status)

    def test_reset_state(self):
        res = self.operator_cloud.share.reset_share_replica_state(
            self.SHARE_REPLICA_ID, 'error'
        )
        self.assertIsNone(res)
        sot = self.user_cloud.share.get_share_replica(self.SHARE_REPLICA_ID)
        self.assertEqual('error', sot.replica_state)

    def test_promote_share_replica(self):
        psr = self.user_cloud.shared_file_system.promote_share_replica(
            self.SHARE_REPLICA_ID
        )
        self.assertIsNone(psr)
        sot = self.user_cloud.share.get_share_replica(self.SHARE_REPLICA_ID)
        self.user_cloud.shared_file_system.wait_for_status(
            sot,
            status='available',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
        )
        sot = self.user_cloud.share.get_share_replica(self.SHARE_REPLICA_ID)
        self.assertEqual('active', sot.replica_state)

    def test_share_replica_resync(self):
        psr = self.operator_cloud.shared_file_system.resync_share_replica(
            self.SHARE_REPLICA_ID
        )
        self.assertIsNone(psr)
        self.user_cloud.shared_file_system.wait_for_status(
            self.SHARE_REPLICA,
            status='in_sync',
            failures=['error'],
            interval=5,
            wait=self._wait_for_timeout,
            attribute='replica_state',
        )
