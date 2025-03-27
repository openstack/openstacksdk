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

import copy
from unittest import mock

from keystoneauth1 import adapter

from openstack.block_storage.v2 import volume
from openstack.tests.unit import base

FAKE_ID = "6685584b-1eac-4da6-b5c3-555430cf68ff"
IMAGE_METADATA = {
    'container_format': 'bare',
    'min_ram': '64',
    'disk_format': 'qcow2',
    'image_name': 'TestVM',
    'image_id': '625d4f2c-cf67-4af3-afb6-c7220f766947',
    'checksum': '64d7c1cd2b6f60c92c14662941cb7913',
    'min_disk': '0',
    'size': '13167616',
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
    "encrypted": "false",
    "OS-SCH-HNT:scheduler_hints": {
        "same_host": [
            "a0cf03a5-d921-4877-bb5c-86d26cf818e1",
            "8c19174f-4220-44f0-824a-cd1eeef10287",
        ]
    },
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

        self.assertDictEqual(
            {
                "name": "name",
                "status": "status",
                "all_projects": "all_tenants",
                "project_id": "project_id",
                "limit": "limit",
                "marker": "marker",
            },
            sot._query_mapping._mapping,
        )

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
        self.assertEqual(
            VOLUME["volume_image_metadata"], sot.volume_image_metadata
        )
        self.assertEqual(VOLUME["size"], sot.size)
        self.assertEqual(VOLUME["imageRef"], sot.image_id)
        self.assertEqual(VOLUME["os-vol-host-attr:host"], sot.host)
        self.assertEqual(
            VOLUME["os-vol-tenant-attr:tenant_id"], sot.project_id
        )
        self.assertEqual(
            VOLUME["os-vol-mig-status-attr:migstat"], sot.migration_status
        )
        self.assertEqual(
            VOLUME["os-vol-mig-status-attr:name_id"], sot.migration_id
        )
        self.assertEqual(VOLUME["replication_status"], sot.replication_status)
        self.assertEqual(
            VOLUME["os-volume-replication:extended_status"],
            sot.extended_replication_status,
        )
        self.assertEqual(
            VOLUME["consistencygroup_id"], sot.consistency_group_id
        )
        self.assertEqual(
            VOLUME["os-volume-replication:driver_data"],
            sot.replication_driver_data,
        )
        self.assertDictEqual(
            VOLUME["OS-SCH-HNT:scheduler_hints"], sot.scheduler_hints
        )
        self.assertFalse(sot.is_encrypted)


class TestVolumeActions(TestVolume):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.status_code = 200
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess._get_connection = mock.Mock(return_value=self.cloud)

    def test_extend(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.extend(self.sess, '20'))

        url = f'volumes/{FAKE_ID}/action'
        body = {"os-extend": {"new_size": "20"}}
        self.sess.post.assert_called_with(url, json=body)

    def test_set_volume_readonly(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.set_readonly(self.sess, True))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-update_readonly_flag': {'readonly': True}}
        self.sess.post.assert_called_with(url, json=body)

    def test_set_volume_readonly_false(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.set_readonly(self.sess, False))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-update_readonly_flag': {'readonly': False}}
        self.sess.post.assert_called_with(url, json=body)

    def test_set_volume_bootable(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.set_bootable_status(self.sess))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-set_bootable': {'bootable': True}}
        self.sess.post.assert_called_with(url, json=body)

    def test_set_volume_bootable_false(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.set_bootable_status(self.sess, False))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-set_bootable': {'bootable': False}}
        self.sess.post.assert_called_with(url, json=body)

    def test_set_image_metadata(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.set_image_metadata(self.sess, {'foo': 'bar'}))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-set_image_metadata': {'foo': 'bar'}}
        self.sess.post.assert_called_with(url, json=body)

    def test_delete_image_metadata(self):
        _volume = copy.deepcopy(VOLUME)
        _volume['metadata'] = {
            'foo': 'bar',
            'baz': 'wow',
        }
        sot = volume.Volume(**_volume)

        self.assertIsNone(sot.delete_image_metadata(self.sess))

        url = f'volumes/{FAKE_ID}/action'
        body_a = {'os-unset_image_metadata': 'foo'}
        body_b = {'os-unset_image_metadata': 'baz'}
        self.sess.post.assert_has_calls(
            [
                mock.call(url, json=body_a),
                mock.call(url, json=body_b),
            ]
        )

    def test_delete_image_metadata_item(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.delete_image_metadata_item(self.sess, 'foo'))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-unset_image_metadata': 'foo'}
        self.sess.post.assert_called_with(url, json=body)

    def test_reset_status(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.reset_status(self.sess, '1', '2', '3'))

        url = f'volumes/{FAKE_ID}/action'
        body = {
            'os-reset_status': {
                'status': '1',
                'attach_status': '2',
                'migration_status': '3',
            }
        }
        self.sess.post.assert_called_with(url, json=body)

    def test_reset_status__single_option(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.reset_status(self.sess, status='1'))

        url = f'volumes/{FAKE_ID}/action'
        body = {
            'os-reset_status': {
                'status': '1',
            }
        }
        self.sess.post.assert_called_with(url, json=body)

    def test_attach_instance(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.attach(self.sess, '1', '2'))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-attach': {'mountpoint': '1', 'instance_uuid': '2'}}
        self.sess.post.assert_called_with(url, json=body)

    def test_detach(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.detach(self.sess, '1'))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-detach': {'attachment_id': '1'}}
        self.sess.post.assert_called_with(url, json=body)

    def test_detach_force(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.detach(self.sess, '1', force=True))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-force_detach': {'attachment_id': '1'}}
        self.sess.post.assert_called_with(url, json=body)

    def test_unmanage(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.unmanage(self.sess))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-unmanage': None}
        self.sess.post.assert_called_with(url, json=body)

    def test_retype(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.retype(self.sess, '1'))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-retype': {'new_type': '1'}}
        self.sess.post.assert_called_with(url, json=body)

    def test_retype_mp(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.retype(self.sess, '1', migration_policy='2'))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-retype': {'new_type': '1', 'migration_policy': '2'}}
        self.sess.post.assert_called_with(url, json=body)

    def test_migrate(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.migrate(self.sess, host='1'))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-migrate_volume': {'host': '1'}}
        self.sess.post.assert_called_with(url, json=body)

    def test_migrate_flags(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(
            sot.migrate(
                self.sess, host='1', force_host_copy=True, lock_volume=True
            )
        )

        url = f'volumes/{FAKE_ID}/action'
        body = {
            'os-migrate_volume': {
                'host': '1',
                'force_host_copy': True,
                'lock_volume': True,
            }
        }
        self.sess.post.assert_called_with(url, json=body)

    def test_complete_migration(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.complete_migration(self.sess, new_volume_id='1'))

        url = f'volumes/{FAKE_ID}/action'
        body = {
            'os-migrate_volume_completion': {'new_volume': '1', 'error': False}
        }
        self.sess.post.assert_called_with(url, json=body)

    def test_complete_migration_error(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(
            sot.complete_migration(self.sess, new_volume_id='1', error=True)
        )

        url = f'volumes/{FAKE_ID}/action'
        body = {
            'os-migrate_volume_completion': {'new_volume': '1', 'error': True}
        }
        self.sess.post.assert_called_with(url, json=body)

    def test_force_delete(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.force_delete(self.sess))

        url = f'volumes/{FAKE_ID}/action'
        body = {'os-force_delete': None}
        self.sess.post.assert_called_with(url, json=body)
