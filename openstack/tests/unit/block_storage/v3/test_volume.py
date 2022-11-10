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

from unittest import mock

from keystoneauth1 import adapter

from openstack.block_storage.v3 import volume
from openstack import exceptions
from openstack.tests.unit import base

FAKE_ID = "6685584b-1eac-4da6-b5c3-555430cf68ff"
IMAGE_METADATA = {
    'container_format': 'bare',
    'min_ram': '64', 'disk_format': u'qcow2',
    'image_name': 'TestVM',
    'image_id': '625d4f2c-cf67-4af3-afb6-c7220f766947',
    'checksum': '64d7c1cd2b6f60c92c14662941cb7913',
    'min_disk': '0', u'size': '13167616'
}

VOLUME = {
    "status": "creating",
    "name": "my_volume",
    "attachments": [],
    "availability_zone": "nova",
    "bootable": "false",
    "created_at": "2015-03-09T12:14:57.233772",
    "updated_at": None,
    "description": "something",
    "volume_type": "some_type",
    "snapshot_id": "93c2e2aa-7744-4fd6-a31a-80c4726b08d7",
    "source_volid": None,
    "imageRef": "some_image",
    "metadata": {},
    "multiattach": False,
    "volume_image_metadata": IMAGE_METADATA,
    "id": FAKE_ID,
    "size": 10,
    "os-vol-host-attr:host": "127.0.0.1",
    "os-vol-tenant-attr:tenant_id": "some tenant",
    "os-vol-mig-status-attr:migstat": "done",
    "os-vol-mig-status-attr:name_id": "93c2e2aa-7744-4fd6-a31a-80c4726b08d7",
    "replication_status": "nah",
    "os-volume-replication:extended_status": "really nah",
    "consistencygroup_id": "123asf-asdf123",
    "os-volume-replication:driver_data": "ahasadfasdfasdfasdfsdf",
    "snapshot_id": "93c2e2aa-7744-4fd6-a31a-80c4726b08d7",
    "encrypted": "false",
    "OS-SCH-HNT:scheduler_hints": {
        "same_host": [
            "a0cf03a5-d921-4877-bb5c-86d26cf818e1",
            "8c19174f-4220-44f0-824a-cd1eeef10287"
        ]
    }
}


class TestVolume(base.TestCase):

    def test_basic(self):
        sot = volume.Volume(VOLUME)
        self.assertEqual("volume", sot.resource_key)
        self.assertEqual("volumes", sot.resources_key)
        self.assertEqual("/volumes", sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

        self.assertDictEqual({"name": "name",
                              "status": "status",
                              "all_projects": "all_tenants",
                              "project_id": "project_id",
                              "created_at": "created_at",
                              "updated_at": "updated_at",
                              "limit": "limit",
                              "marker": "marker"},
                             sot._query_mapping._mapping)

    def test_create(self):
        sot = volume.Volume(**VOLUME)
        self.assertEqual(VOLUME["id"], sot.id)
        self.assertEqual(VOLUME["status"], sot.status)
        self.assertEqual(VOLUME["attachments"], sot.attachments)
        self.assertEqual(VOLUME["availability_zone"], sot.availability_zone)
        self.assertFalse(sot.is_bootable)
        self.assertEqual(VOLUME["created_at"], sot.created_at)
        self.assertEqual(VOLUME["updated_at"], sot.updated_at)
        self.assertEqual(VOLUME["description"], sot.description)
        self.assertEqual(VOLUME["volume_type"], sot.volume_type)
        self.assertEqual(VOLUME["snapshot_id"], sot.snapshot_id)
        self.assertEqual(VOLUME["source_volid"], sot.source_volume_id)
        self.assertEqual(VOLUME["metadata"], sot.metadata)
        self.assertEqual(VOLUME["multiattach"], sot.is_multiattach)
        self.assertEqual(VOLUME["volume_image_metadata"],
                         sot.volume_image_metadata)
        self.assertEqual(VOLUME["size"], sot.size)
        self.assertEqual(VOLUME["imageRef"], sot.image_id)
        self.assertEqual(VOLUME["os-vol-host-attr:host"], sot.host)
        self.assertEqual(VOLUME["os-vol-tenant-attr:tenant_id"],
                         sot.project_id)
        self.assertEqual(VOLUME["os-vol-mig-status-attr:migstat"],
                         sot.migration_status)
        self.assertEqual(VOLUME["os-vol-mig-status-attr:name_id"],
                         sot.migration_id)
        self.assertEqual(VOLUME["replication_status"],
                         sot.replication_status)
        self.assertEqual(
            VOLUME["os-volume-replication:extended_status"],
            sot.extended_replication_status)
        self.assertEqual(VOLUME["consistencygroup_id"],
                         sot.consistency_group_id)
        self.assertEqual(VOLUME["os-volume-replication:driver_data"],
                         sot.replication_driver_data)
        self.assertFalse(sot.is_encrypted)
        self.assertDictEqual(VOLUME["OS-SCH-HNT:scheduler_hints"],
                             sot.scheduler_hints)


class TestVolumeActions(TestVolume):

    def setUp(self):
        super(TestVolumeActions, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.status_code = 200
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.default_microversion = '3.0'
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess._get_connection = mock.Mock(return_value=self.cloud)

    def test_extend(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.extend(self.sess, '20'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {"os-extend": {"new_size": "20"}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_set_volume_readonly(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.set_readonly(self.sess, True))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-update_readonly_flag': {'readonly': True}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_set_volume_readonly_false(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.set_readonly(self.sess, False))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-update_readonly_flag': {'readonly': False}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_set_volume_bootable(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.set_bootable_status(self.sess))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-set_bootable': {'bootable': True}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_set_volume_bootable_false(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.set_bootable_status(self.sess, False))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-set_bootable': {'bootable': False}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_reset_status(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.reset_status(self.sess, '1', '2', '3'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-reset_status': {'status': '1', 'attach_status': '2',
                                    'migration_status': '3'}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    @mock.patch('openstack.utils.require_microversion', autospec=True,
                side_effect=[exceptions.SDKException()])
    def test_revert_to_snapshot_before_340(self, mv_mock):
        sot = volume.Volume(**VOLUME)

        self.assertRaises(
            exceptions.SDKException,
            sot.revert_to_snapshot,
            self.sess,
            '1'
        )

    @mock.patch('openstack.utils.require_microversion', autospec=True,
                side_effect=[None])
    def test_revert_to_snapshot_after_340(self, mv_mock):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.revert_to_snapshot(self.sess, '1'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'revert': {'snapshot_id': '1'}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)
        mv_mock.assert_called_with(self.sess, '3.40')

    def test_attach_instance(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.attach(self.sess, '1', instance='2'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-attach': {'mountpoint': '1', 'instance_uuid': '2'}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_attach_host(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.attach(self.sess, '1', host_name='2'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-attach': {'mountpoint': '1', 'host_name': '2'}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_attach_error(self):
        sot = volume.Volume(**VOLUME)

        self.assertRaises(
            ValueError,
            sot.attach,
            self.sess,
            '1')

    def test_detach(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.detach(self.sess, '1'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-detach': {'attachment_id': '1'}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_detach_force(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(
            sot.detach(self.sess, '1', force=True, connector={'a': 'b'}))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-force_detach': {'attachment_id': '1',
                                    'connector': {'a': 'b'}}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_unmanage(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.unmanage(self.sess))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-unmanage': {}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_retype(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.retype(self.sess, '1'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-retype': {'new_type': '1'}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_retype_mp(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.retype(self.sess, '1', migration_policy='2'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-retype': {'new_type': '1', 'migration_policy': '2'}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_migrate(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.migrate(self.sess, host='1'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-migrate_volume': {'host': '1'}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_migrate_flags(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.migrate(self.sess, host='1',
                                      force_host_copy=True, lock_volume=True))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-migrate_volume': {'host': '1', 'force_host_copy': True,
                                      'lock_volume': True}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    @mock.patch('openstack.utils.require_microversion', autospec=True,
                side_effect=[None])
    def test_migrate_cluster(self, mv_mock):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.migrate(self.sess, cluster='1',
                                      force_host_copy=True, lock_volume=True))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-migrate_volume': {'cluster': '1', 'force_host_copy': True,
                                      'lock_volume': True}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)
        mv_mock.assert_called_with(self.sess, '3.16')

    def test_complete_migration(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.complete_migration(self.sess, new_volume_id='1'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-migrate_volume_completion': {'new_volume': '1', 'error':
                                                 False}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_complete_migration_error(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.complete_migration(
            self.sess, new_volume_id='1', error=True))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-migrate_volume_completion': {'new_volume': '1', 'error':
                                                 True}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_force_delete(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.force_delete(self.sess))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-force_delete': {}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_upload_image(self):
        sot = volume.Volume(**VOLUME)

        self.resp = mock.Mock()
        self.resp.body = {'os-volume_upload_image': {'a': 'b'}}
        self.resp.status_code = 200
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess.post = mock.Mock(return_value=self.resp)

        self.assertDictEqual({'a': 'b'}, sot.upload_to_image(self.sess, '1'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-volume_upload_image': {
            'image_name': '1',
            'force': False
        }}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    @mock.patch('openstack.utils.require_microversion', autospec=True,
                side_effect=[None])
    def test_upload_image_args(self, mv_mock):
        sot = volume.Volume(**VOLUME)

        self.resp = mock.Mock()
        self.resp.body = {'os-volume_upload_image': {'a': 'b'}}
        self.resp.status_code = 200
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess.post = mock.Mock(return_value=self.resp)

        self.assertDictEqual(
            {'a': 'b'},
            sot.upload_to_image(self.sess, '1', disk_format='2',
                                container_format='3', visibility='4',
                                protected='5'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-volume_upload_image': {
            'image_name': '1',
            'force': False,
            'disk_format': '2',
            'container_format': '3',
            'visibility': '4',
            'protected': '5'
        }}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)
        mv_mock.assert_called_with(self.sess, '3.1')

    def test_reserve(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.reserve(self.sess))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-reserve': {}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_unreserve(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.unreserve(self.sess))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-unreserve': {}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_begin_detaching(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.begin_detaching(self.sess))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-begin_detaching': {}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_abort_detaching(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.abort_detaching(self.sess))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-roll_detaching': {}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_init_attachment(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.init_attachment(self.sess, {'a': 'b'}))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-initialize_connection': {'connector': {'a': 'b'}}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)

    def test_terminate_attachment(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.terminate_attachment(self.sess, {'a': 'b'}))

        url = 'volumes/%s/action' % FAKE_ID
        body = {'os-terminate_connection': {'connector': {'a': 'b'}}}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion)
