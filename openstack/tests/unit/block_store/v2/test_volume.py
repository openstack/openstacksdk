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
import datetime

import testtools

from openstack.block_store.v2 import volume

FAKE_ID = "6685584b-1eac-4da6-b5c3-555430cf68ff"

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
    "id": FAKE_ID,
    "size": 10
}

DETAILS = {
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
}

VOLUME_DETAIL = copy.copy(VOLUME)
VOLUME_DETAIL.update(DETAILS)


class TestVolume(testtools.TestCase):

    def test_basic(self):
        sot = volume.Volume(VOLUME)
        self.assertEqual("volume", sot.resource_key)
        self.assertEqual("volumes", sot.resources_key)
        self.assertEqual("id", sot.id_attribute)
        self.assertEqual("/volumes", sot.base_path)
        self.assertEqual("volume", sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_retrieve)
        self.assertTrue(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_create(self):
        sot = volume.Volume(VOLUME)
        self.assertEqual(VOLUME["id"], sot.id)
        self.assertEqual(VOLUME["status"], sot.status)
        self.assertEqual(VOLUME["attachments"], sot.attachments)
        self.assertEqual(VOLUME["availability_zone"], sot.availability_zone)
        self.assertFalse(sot.is_bootable)
        dt = datetime.datetime(2015, 3, 9, 12, 14, 57, 233772).replace(
            tzinfo=None)
        self.assertEqual(dt, sot.created_at.replace(tzinfo=None))
        self.assertEqual(VOLUME["description"], sot.description)
        self.assertEqual(VOLUME["volume_type"], sot.volume_type)
        self.assertEqual(VOLUME["snapshot_id"], sot.snapshot_id)
        self.assertEqual(VOLUME["source_volid"], sot.source_volume_id)
        self.assertEqual(VOLUME["metadata"], sot.metadata)
        self.assertEqual(VOLUME["size"], sot.size)
        self.assertEqual(VOLUME["imageRef"], sot.image_id)


class TestVolumeDetail(testtools.TestCase):

    def test_basic(self):
        sot = volume.VolumeDetail(VOLUME_DETAIL)
        self.assertIsInstance(sot, volume.Volume)
        self.assertEqual("/volumes/detail", sot.base_path)

    def test_create(self):
        sot = volume.VolumeDetail(VOLUME_DETAIL)
        self.assertEqual(VOLUME_DETAIL["os-vol-host-attr:host"], sot.host)
        self.assertEqual(VOLUME_DETAIL["os-vol-tenant-attr:tenant_id"],
                         sot.project_id)
        self.assertEqual(VOLUME_DETAIL["os-vol-mig-status-attr:migstat"],
                         sot.migration_status)
        self.assertEqual(VOLUME_DETAIL["os-vol-mig-status-attr:name_id"],
                         sot.migration_id)
        self.assertEqual(VOLUME_DETAIL["replication_status"],
                         sot.replication_status)
        self.assertEqual(
            VOLUME_DETAIL["os-volume-replication:extended_status"],
            sot.extended_replication_status)
        self.assertEqual(VOLUME_DETAIL["consistencygroup_id"],
                         sot.consistency_group_id)
        self.assertEqual(VOLUME_DETAIL["os-volume-replication:driver_data"],
                         sot.replication_driver_data)
        self.assertFalse(sot.is_encrypted)
