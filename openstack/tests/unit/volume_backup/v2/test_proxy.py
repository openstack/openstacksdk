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

from openstack.tests.unit.test_proxy_base3 import BaseProxyTestCase
from openstack.volume_backup.v2 import _proxy
from openstack.volume_backup.v2 import backup as _backup
from openstack.volume_backup.v2 import backup_policy as _backup_policy
from openstack.volume_backup import volume_backup_service


class TestVolumeBackupProxy(BaseProxyTestCase):
    def __init__(self, *args, **kwargs):
        super(TestVolumeBackupProxy, self).__init__(
            *args,
            proxy_class=_proxy.Proxy,
            service_class=volume_backup_service.VolumeBackupService,
            **kwargs)


class TestCloudBackup(TestVolumeBackupProxy):
    def __init__(self, *args, **kwargs):
        super(TestCloudBackup, self).__init__(*args, **kwargs)

    def test_create_backup(self):
        self.mock_response_json_values({
            "id": "70a599e0-31e7-49b7-b260-868f441e862b"
        })

        data = {
            "name": "backup1",
            "volume_id": "c68ae7fb-0aa5-4a97-ab01-ed02c5b7e768",
            "description": "Backups_Demon"
        }

        job = self.proxy.create_backup(**data)
        expect_post_json = {
            "backup": {
                "volume_id": "c68ae7fb-0aa5-4a97-ab01-ed02c5b7e768",
                "name": "backup1",
                "description": "Backups_Demon"
            }
        }
        self.assert_session_post_with("/cloudbackups", json=expect_post_json)
        self.assertIsInstance(job, _backup.CloudBackup)
        self.assertEqual("70a599e0-31e7-49b7-b260-868f441e862b",
                         job.job_id)

    def test_create_native_backup(self):
        self.mock_response_json_file_values(
            "create_native_backup_response.json")

        data = {
            "volume_id": "c68ae7fb-0aa5-4a97-ab01-ed02c5b7e768",
            "snapshot_id": "2bb856e1-b3d8-4432-a858-09e4ce939389",
            "name": "backup1",
            "description": "Backup_Demo"
        }

        backup = self.proxy.create_native_backup(**data)
        expect_post_json = {
            "backup": {
                "volume_id": "c68ae7fb-0aa5-4a97-ab01-ed02c5b7e768",
                "snapshot_id": "2bb856e1-b3d8-4432-a858-09e4ce939389",
                "name": "backup1",
                "description": "Backup_Demo"
            }
        }
        self.assert_session_post_with("/backups", json=expect_post_json)
        self.assertIsInstance(backup, _backup.Backup)
        self.assertEqual("54ba0e69-48a0-4a77-9cdf-a7979a7e2648",
                         backup.id)
        self.assertEqual("backup1", backup.name)

    def test_delete_backup_with_id(self):
        self.proxy.delete_backup("some-backup-id")
        self.assert_session_delete("backups/some-backup-id")

    def test_delete_backup_with_instance(self):
        self.proxy.delete_backup(_backup.Backup(id="some-backup-id"))
        self.assert_session_delete("backups/some-backup-id")

    def test_restore_backup(self):
        self.mock_response_json_values({
            "id": "70a599e0-31e7-49b7-b260-868f441e862b"
        })

        job = self.proxy.restore_backup(
            "some-backup-id", "c96e4a94-927a-425c-8795-63f9964cfebd")
        expect_post_json = {
            "restore": {
                "volume_id": "c96e4a94-927a-425c-8795-63f9964cfebd"
            }
        }
        self.assert_session_post_with(
            "cloudbackups/some-backup-id/restore", json=expect_post_json)
        self.assertIsInstance(job, _backup.CloudBackup)
        self.assertEqual("70a599e0-31e7-49b7-b260-868f441e862b",
                         job.job_id)

    def test_list_backup(self):
        query = {
            "name": "some-backup",
            "status": "available",
            "volume_id": "0781095c-b8ab-4ce5-99f3-4c5f6ff75319",
            "limit": 10
        }
        self.mock_response_json_file_values("list_backups.json")
        backups = list(self.proxy.backups(**query))

        transferred_query = {
            "name": "some-backup",
            "status": "available",
            "volume_id": "0781095c-b8ab-4ce5-99f3-4c5f6ff75319",
            "limit": 10
        }
        self.assert_session_list_with("/backups", params=transferred_query)
        self.assertEqual(2, len(backups))
        backup = backups[0]
        self.assertEqual("1d1139d8-8989-49d3-8aa1-83eb691e6db2", backup.id)
        self.assertIsNone(backup.name)

    def test_list_backup_detail(self):
        query = {
            "name": "some-backup",
            "status": "available",
            "volume_id": "0781095c-b8ab-4ce5-99f3-4c5f6ff75319",
            "limit": 10
        }
        self.mock_response_json_file_values("list_backup_details.json")
        backups = list(self.proxy.backups(details=True, **query))

        transferred_query = {
            "name": "some-backup",
            "status": "available",
            "volume_id": "0781095c-b8ab-4ce5-99f3-4c5f6ff75319",
            "limit": 10
        }
        self.assert_session_list_with("/backups/detail",
                                      params=transferred_query)
        self.assertEqual(3, len(backups))
        backup = backups[0]
        self.assertIsInstance(backup, _backup.BackupDetail)

        self.assertEqual("error", backup.status)
        self.assertIsNone(backup.description)
        self.assertIsNone(backup.availability_zone)
        self.assertEqual("2748f2f2-4394-4e6e-af8d-8dd34496c024",
                         backup.volume_id)

        self.assertEqual(("Connection to swift failed: "
                          "[Errno 111] ECONNREFUSED"),
                         backup.fail_reason)
        self.assertEqual("1d1139d8-8989-49d3-8aa1-83eb691e6db2",
                         backup.id)
        self.assertEqual(1, backup.size)
        self.assertIsNone(backup.object_count)
        self.assertEqual("volumebackups", backup.container)
        self.assertIsNone(backup.name)
        self.assertEqual("2013-06-27T08:48:03.000000", backup.created_at)
        self.assertEqual("b23b579f08c84228b9b4673c46f0c442",
                         backup.tenant_id)

    def test_get_backup(self):
        self.mock_response_json_file_values("get_backup.json")
        backup = self.proxy.get_backup("backup-id")
        self.session.get.assert_called_once_with(
            "backups/backup-id",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )

        self.assertIsInstance(backup, _backup.Backup)

        self.assertEqual("error", backup.status)
        self.assertIsNone(backup.description)
        self.assertIsNone(backup.availability_zone)
        self.assertEqual("2748f2f2-4394-4e6e-af8d-8dd34496c024",
                         backup.volume_id)

        self.assertEqual(("Connection to swift failed: "
                          "[Errno 111] ECONNREFUSED"),
                         backup.fail_reason)
        self.assertEqual("1d1139d8-8989-49d3-8aa1-83eb691e6db2",
                         backup.id)
        self.assertEqual(1, backup.size)
        self.assertIsNone(backup.object_count)
        self.assertEqual("volumebackups", backup.container)
        self.assertIsNone(backup.name)
        self.assertEqual("2013-06-27T08:48:03.000000", backup.created_at)
        self.assertEqual("b23b579f08c84228b9b4673c46f0c442",
                         backup.tenant_id)


class TestBackupPolicy(TestVolumeBackupProxy):
    def __init__(self, *args, **kwargs):
        super(TestBackupPolicy, self).__init__(*args, **kwargs)

    def test_list_backup_policy(self):
        self.mock_response_json_file_values("list_backup_policies.json")
        policies = list(self.proxy.backup_policies())
        self.assert_session_list_with("/backuppolicy",
                                      params={})
        self.assertEqual(2, len(policies))
        policy = policies[0]
        self.assertIsInstance(policy, _backup_policy.BackupPolicy)
        self.assertEqual("XX", policy.id)
        self.assertEqual("plan01", policy.name)
        self.assertEqual(0, policy.policy_resource_count)
        scheduled_policy = policy.scheduled_policy
        self.assertIsInstance(scheduled_policy, _backup_policy.SchedulePolicy)
        self.assertEqual(False,
                         scheduled_policy.remain_first_backup_of_curMonth)
        self.assertEqual(10, scheduled_policy.rentention_num)
        self.assertEqual(1, scheduled_policy.frequency)
        self.assertEqual("12:00", scheduled_policy.start_time)
        self.assertEqual("ON", scheduled_policy.status)

        self.assertTrue(policies[1].scheduled_policy
                        .remain_first_backup_of_curMonth)

    def test_create_backup_policy(self):
        self.mock_response_json_values({
            "backup_policy_id": "af8a20b0-117d-4fc3-ae53-aa3968a4f870"
        })

        scheduled_policy = {
            "remain_first_backup_of_curMonth": True,
            "rentention_num": 10,
            "frequency": 1,
            "start_time": "12:00",
            "status": "ON"
        }

        policy = self.proxy.create_backup_policy("backup_policy_name",
                                                 **scheduled_policy)
        expect_post_json = {
            "backup_policy_name": "backup_policy_name",
            "scheduled_policy": {
                "remain_first_backup_of_curMonth": "Y",
                "rentention_num": 10,
                "frequency": 1,
                "start_time": "12:00",
                "status": "ON"
            }
        }
        self.assert_session_post_with("/backuppolicy",
                                      json=expect_post_json)
        self.assertEqual("af8a20b0-117d-4fc3-ae53-aa3968a4f870", policy.id)

    def test_update_backup_policy(self):
        self.mock_response_json_values({
            "backup_policy_id": "af8a20b0-117d-4fc3-ae53-aa3968a4f870"
        })
        attrs = self.get_file_content("update_policy.json")

        self.proxy.update_backup_policy("some-policy-id", **attrs)
        expected_json = {
            "backup_policy_name": "policy_01",
            "scheduled_policy": {
                "remain_first_backup_of_curMonth": "Y",
                "rentention_num": 10,
                "frequency": 1,
                "start_time": "12:00",
                "status": "ON"
            }
        }
        self.assert_session_put_with("backuppolicy/some-policy-id",
                                     json=expected_json)

    def test_delete_backup_policy_with_id(self):
        self.proxy.delete_backup_policy("some-config-id")
        self.assert_session_delete("backuppolicy/some-config-id")

    def test_link_resource_to_policy(self):
        self.mock_response_json_file_values("link_resources.json")
        policy = _backup_policy.BackupPolicy(id="policy-id")
        resources = ["volume-id-1", "volume-id-2"]
        linked_resources = self.proxy.link_resources_to_policy(policy,
                                                               resources)
        self.assert_session_post_with("/backuppolicyresources",
                                      json={
                                          "backup_policy_id": "policy-id",
                                          "resources": [{
                                              "resource_id": "volume-id-1",
                                              "resource_type": "volume"
                                          }, {
                                              "resource_id": "volume-id-2",
                                              "resource_type": "volume"
                                          }]
                                      })

        self.assertEqual(2, len(linked_resources))
        success = linked_resources[0]
        self.assertEqual("bce8d47a-af17-4169-901f-4c7ae9f29c2c",
                         success.resource_id)
        self.assertEqual("pod01.eu-de-01sa-brazil-1cn-north-1",
                         success.os_vol_host_attr)
        self.assertEqual("eu-de-01sa-brazil-1cn-north-1",
                         success.availability_zone)
        self.assertEqual("volume", success.resource_type)
        self.assertTrue(success.success)

        success = linked_resources[1]
        self.assertEqual("volume-id-2", success.resource_id)
        self.assertEqual("pod01.eu-de-01sa-brazil-1cn-north-1",
                         success.os_vol_host_attr)
        self.assertEqual("eu-de-01sa-brazil-1cn-north-1",
                         success.availability_zone)
        self.assertEqual("volume", success.resource_type)
        self.assertEqual("VBS.0002", success.code)
        self.assertEqual("xxxxx", success.message)
        self.assertFalse(success.success)

    def test_unlink_resource_of_policy(self):
        self.mock_response_json_file_values("unlink_resources.json")
        policy = _backup_policy.BackupPolicy(id="policy-id")
        resources = ["volume-id-1", "volume-id-2"]
        linked_resources = self.proxy.unlink_resources_of_policy(policy,
                                                                 resources)
        self.assert_session_post_with(
            "backuppolicyresources/policy-id/deleted_resources",
            json={
                "resources": [{
                    "resource_id": "volume-id-1"
                }, {
                    "resource_id": "volume-id-2"
                }]
            })

        self.assertEqual(2, len(linked_resources))
        success = linked_resources[0]
        self.assertEqual("bce8d47a-af17-4169-901f-4c7ae9f29c2c",
                         success.resource_id)
        self.assertTrue(success.success)

        success = linked_resources[1]
        self.assertEqual("volume-id-2", success.resource_id)
        self.assertEqual("VBS.0002", success.code)
        self.assertEqual("xxxxx", success.message)
        self.assertFalse(success.success)

    def test_execute_policy(self):
        policy = _backup_policy.BackupPolicy(id="policy-id")
        self.proxy.execute_policy(policy)
        self.assert_session_post_with("backuppolicy/policy-id/action",
                                      json=None)

    def test_enable_policy(self):
        self.mock_response_json_file_values("update_policy.json")
        policy = _backup_policy.BackupPolicy(id="policy-id")
        self.proxy.enable_policy(policy)
        self.assert_session_put_with("backuppolicy/policy-id",
                                     json={
                                         "scheduled_policy": {
                                             "status": "ON"
                                         }
                                     })

    def test_disable_policy(self):
        self.mock_response_json_file_values("update_policy.json")
        policy = _backup_policy.BackupPolicy(id="policy-id")
        self.proxy.disable_policy(policy)
        self.assert_session_put_with("backuppolicy/policy-id",
                                     json={
                                         "scheduled_policy": {
                                             "status": "OFF"
                                         }
                                     })

    def test_list_task(self):
        query = {
            "sort_dir": "asc",
            "sort_key": "created_at",
            "status": "RUNNING",
            "id": "0781095c-b8ab-4ce5-99f3-4c5f6ff75319",
            "limit": 10,
            "offset": 10
        }
        self.mock_response_json_file_values("list_tasks.json")
        tasks = list(self.proxy.tasks("policy-id", **query))

        transferred_query = {
            "sort_dir": "asc",
            "sort_key": "created_at",
            "status": "RUNNING",
            "job_id": "0781095c-b8ab-4ce5-99f3-4c5f6ff75319",
            "limit": 10,
            "offset": 10
        }
        self.assert_session_list_with("/backuppolicy/policy-id/backuptasks",
                                      params=transferred_query)
        self.assertEqual(2, len(tasks))
        task = tasks[0]
        self.assertEqual("RUNNING", task.status)
        self.assertEqual("0781095c-b8ab-4ce5-99f3-4c5f6ff75319", task.id)
        self.assertEqual("2016-12-03T06:24:34.467", task.created_at)
        self.assertEqual("autobk_a61d", task.backup_name)
        self.assertEqual("f47a4ab5-11f5-4509-97f5-80ce0dd74e37",
                         task.resource_id)
        self.assertEqual("volume", task.resource_type)
