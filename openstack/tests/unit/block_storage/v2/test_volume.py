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

from openstack.block_storage.v2 import volume
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
    "snapshot_id": "93c2e2aa-7744-4fd6-a31a-80c4726b08d7",
    "encrypted": "false"
}


class TestVolume(base.TestCase):

    def setUp(self):
        super(TestVolume, self).setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.sess = mock.Mock()
        self.sess.post = mock.Mock(return_value=self.resp)

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
        self.assertEqual(VOLUME["description"], sot.description)
        self.assertEqual(VOLUME["volume_type"], sot.volume_type)
        self.assertEqual(VOLUME["snapshot_id"], sot.snapshot_id)
        self.assertEqual(VOLUME["source_volid"], sot.source_volume_id)
        self.assertEqual(VOLUME["metadata"], sot.metadata)
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

    def test_extend(self):
        sot = volume.Volume(**VOLUME)

        self.assertIsNone(sot.extend(self.sess, '20'))

        url = 'volumes/%s/action' % FAKE_ID
        body = {"os-extend": {"new_size": "20"}}
        headers = {'Accept': ''}
        self.sess.post.assert_called_with(url, json=body, headers=headers)
