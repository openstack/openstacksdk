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

from openstack.auto_scaling import auto_scaling_service
from openstack.auto_scaling.v1 import _proxy
from openstack.auto_scaling.v1 import activity as _activity_log
from openstack.auto_scaling.v1 import config as _config
from openstack.auto_scaling.v1 import group as _group
from openstack.auto_scaling.v1 import instance as _instance
from openstack.auto_scaling.v1 import policy as _policy
from openstack.auto_scaling.v1 import quota as _quota
from openstack.tests.unit.test_proxy_base3 import BaseProxyTestCase


class TestAutoScalingProxy(BaseProxyTestCase):
    def __init__(self, *args, **kwargs):
        super(TestAutoScalingProxy, self).__init__(
            *args,
            proxy_class=_proxy.Proxy,
            service_class=auto_scaling_service.AutoScalingService,
            **kwargs)


class TestAutoScalingConfig(TestAutoScalingProxy):
    def __init__(self, *args, **kwargs):
        super(TestAutoScalingConfig, self).__init__(*args, **kwargs)

    def test_list_config(self):
        query = {
            "name": "as_config_name",
            "image_id": "image-ref-id",
            "marker": 0
        }
        self.mock_response_json_file_values("list_config.json")
        configs = list(self.proxy.configs(**query))

        transferred_query = {
            "scaling_configuration_name": "as_config_name",
            "image_id": "image-ref-id",
            "start_number": 0
        }
        self.assert_session_list_with("/scaling_configuration",
                                      params=transferred_query)

        self.assertEqual(2, len(configs))

        config1 = configs[0]
        self.assertIsInstance(config1, _config.Config)
        self.assertEqual("6afe46f9-7d3d-4046-8748-3b2a1085ad86",
                         config1.id)
        self.assertEqual("config_name_1", config1.name)
        self.assertEqual("STANDBY", config1.status)
        self.assertEqual("2015-07-23T01:04:07Z", config1.create_time)

        instance_config = config1.instance_config
        self.assertIsNone(instance_config.id)
        self.assertIsNone(instance_config.name)
        self.assertEqual("103", instance_config.flavor_id)
        self.assertEqual("37ca2b35-6fc7-47ab-93c7-900324809c5c",
                         instance_config.image_id)
        self.assertEqual("keypair02", instance_config.key_name)
        disk = [{"size": 40, "volume_type": "SATA", "disk_type": "SYS"},
                {"size": 100, "volume_type": "SATA", "disk_type": "DATA"}]
        self.assertEqual(disk, instance_config.disk)

        def test_create_config(self):
            self.mock_response_json_values({
                "scaling_configuration_id":
                    "f8327883-6a07-4497-9a61-68c03e8e72a2"
            })

            _intance_config = {
                "flavor_id": "103",
                "image_id": "627a1223-2ca3-46a7-8d5f-7aef22c74ee6",
                "disk": [{
                    "size": 40,
                    "volume_type": "SATA",
                    "disk_type": "SYS"
                }],
                "personality": [{
                    "path": "/etc/profile.d/authentication.sh",
                    "content": "some-base64-text-content"
                }, {
                    "path": "/etc/profile.d/env.sh",
                    "content": "some-base64-text-content"
                }],
                "metadata": {
                    "key1": "value1",
                    "tag": "app"
                },
                "key_name": "100vm_key"
            }

            config = self.proxy.create_config("as_config_name",
                                              **_intance_config)
            expect_post_json = {
                "scaling_configuration_name": "as_config_name",
                "instance_config": {
                    "flavorRef": "103",
                    "imageRef": "627a1223-2ca3-46a7-8d5f-7aef22c74ee6",
                    "disk": [
                        {
                            "size": 40,
                            "volume_type": "SATA",
                            "disk_type": "SYS"
                        }
                    ],
                    "personality": [{
                        "path": "/etc/profile.d/authentication.sh",
                        "content": "some-base64-text-content"
                    }, {
                        "path": "/etc/profile.d/env.sh",
                        "content": "some-base64-text-content"
                    }],
                    "metadata": {
                        "key1": "value1",
                        "tag": "app"
                    },
                    "key_name": "100vm_key"
                }
            }
            self.assert_session_post_with("/scaling_configuration",
                                          json=expect_post_json)
            self.assertEqual("f8327883-6a07-4497-9a61-68c03e8e72a2", config.id)

        def test_get_config_with_id(self):
            self.mock_response_json_file_values("get_config.json")
            config = self.proxy.get_config("some-config-id")
            self.session.get.assert_called_once_with(
                "scaling_configuration/some-config-id",
                endpoint_filter=self.service,
                endpoint_override=self.service.get_endpoint_override(),
            )
            self.assertIsInstance(config, _config.Config)
            self.assertEqual("6afe46f9-7d3d-4046-8748-3b2a1085ad86",
                             config.id)
            self.assertEqual("config_name_1", config.name)
            self.assertEqual("2015-07-23T01:04:07Z", config.create_time)
            self.assertIsInstance(config.instance_config,
                                  _config.InstanceConfig)
            ic = config.instance_config
            self.assertEqual("37ca2b35-6fc7-47ab-93c7-900324809c5c",
                             ic.image_id)
            self.assertEqual("103", ic.flavor_id)
            self.assertEqual("keypair01", ic.key_name)
            self.assertEqual([{"size": 40,
                               "volume_type": "SATA",
                               "disk_type": "SYS"},
                              {"size": 100,
                               "volume_type": "SATA",
                               "disk_type": "DATA"}],
                             ic.disk)

        def test_delete_config_with_id(self):
            self.proxy.delete_config("some-config-id")
            self.assert_session_delete("scaling_configuration/some-config-id")

        def test_delete_config_with_instance(self):
            self.proxy.delete_config(_config.Config(id="some-config-id"))
            self.assert_session_delete("scaling_configuration/some-config-id")

        def test_batch_delete_configs(self):
            configs = [
                "config-id-1",
                "config-id-2",
                _config.Config(id="config-id-3")
            ]
            self.proxy.batch_delete_configs(configs)
            self.assert_session_post_with("/scaling_configurations",
                                          headers={"Accept": "*"},
                                          json={
                                              "scaling_configuration_id": [
                                                  "config-id-1",
                                                  "config-id-2",
                                                  "config-id-3"
                                              ]
                                          })


class TestAutoScalingGroup(TestAutoScalingProxy):
    def __init__(self, *args, **kwargs):
        super(TestAutoScalingGroup, self).__init__(*args, **kwargs)

    def test_list_group(self):
        query = {
            "name": "as_group_name",
            "scaling_configuration_id": "as-config-id",
            "marker": 0
        }
        self.mock_response_json_file_values("list_group.json")
        groups = list(self.proxy.groups(**query))

        transferred_query = {
            "scaling_group_name": "as_group_name",
            "scaling_configuration_id": "as-config-id",
            "start_number": 0
        }
        self.assert_session_list_with("/scaling_group",
                                      params=transferred_query)

        self.assertEqual(1, len(groups))

        group1 = groups[0]
        self.assertIsInstance(group1, _group.Group)
        self.assertEqual("77a7a397-7d2f-4e79-9da9-6a35e2709150",
                         group1.id)
        self.assertEqual("healthCheck", group1.name)
        self.assertEqual("INSERVICE", group1.status)
        self.assertEqual("1d281494-6085-4579-b817-c1f813be835f",
                         group1.scaling_configuration_id)

        self.assertEqual(0, group1.current_instance_number)
        self.assertEqual(1, group1.desire_instance_number)
        self.assertEqual(0, group1.min_instance_number)
        self.assertEqual(500, group1.max_instance_number)
        self.assertEqual(300, group1.cool_down_time)
        self.assertEqual("f06c0112570743b51c0e8fbe1f235bab",
                         group1.lb_listener_id)
        self.assertEqual("2015-07-23T02:46:29Z", group1.create_time)
        self.assertEqual("863ccae2-ee85-4d27-bc5b-3ba2a198a9e2",
                         group1.vpc_id)
        self.assertEqual([{"id": "8a4b1d5b-0054-419f-84b1-5c8a59ebc829"}],
                         group1.security_groups)
        self.assertEqual("ELB_AUDIT", group1.health_periodic_audit_method)
        self.assertEqual("5", group1.health_periodic_audit_time)
        self.assertEqual("OLD_CONFIG_OLD_INSTANCE",
                         group1.instance_terminate_policy)
        self.assertEqual(False, group1.is_scaling)
        self.assertEqual(False, group1.delete_publicip)
        self.assertEqual(["EMAIL"], group1.notifications)

    def test_create_group(self):
        self.mock_response_json_values({
            "scaling_group_id": "a8327883-6b07-4497-9c61-68d03ee193a1"
        })

        attrs = self.get_file_content("create_group.json")
        group = self.proxy.create_group(**attrs)
        expect_post_json = {
            "scaling_group_name": "GroupNameTest",
            "scaling_configuration_id":
                "47683a91-93ee-462a-a7d7-484c006f4440",
            "desire_instance_number": 10,
            "min_instance_number": 2,
            "max_instance_number": 20,
            "cool_down_time": 200,
            "health_periodic_audit_method": "NOVA_AUDIT",
            "health_periodic_audit_time": "5",
            "instance_terminate_policy": "OLD_CONFIG_OLD_INSTANCE",
            "vpc_id": "a8327883-6b07-4497-9c61-68d03ee193a",
            "networks": [{
                "id": "3cd35bca-5a10-416f-8994-f79169559870"
            }],
            "notifications": [
                "EMAIL"
            ],
            "security_groups": [{
                "id": "23b7b999-0a30-4b48-ae8f-ee201a88a6ab"
            }]
        }
        self.assert_session_post_with("/scaling_group",
                                      json=expect_post_json)
        self.assertEqual("a8327883-6b07-4497-9c61-68d03ee193a1", group.id)

    def test_get_group_with_id(self):
        self.mock_response_json_file_values("get_group.json")
        group = self.proxy.get_group("some-group-id")
        self.session.get.assert_called_once_with(
            "scaling_group/some-group-id",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )

        self.assertIsInstance(group, _group.Group)
        self.assertEqual("d4e50321-3777-4135-97f8-9f5e9714a4b0", group.id)
        self.assertEqual("api_gateway_modify", group.name)
        self.assertEqual("2015-09-01T08:36:10Z", group.create_time)
        self.assertEqual("INSERVICE", group.status)
        self.assertEqual("53579851-3841-418d-a97b-9cecdb663a90",
                         group.scaling_configuration_id)
        self.assertEqual("press", group.scaling_configuration_name)

        self.assertEqual(7, group.current_instance_number)
        self.assertEqual(8, group.desire_instance_number)
        self.assertEqual(0, group.min_instance_number)
        self.assertEqual(100, group.max_instance_number)
        self.assertEqual(900, group.cool_down_time)
        self.assertIsNone(group.lb_listener_id)
        self.assertIsNone(group.detail)
        self.assertEqual("3e22f934-800d-4bb4-a588-0b9a76108190",
                         group.vpc_id)
        self.assertEqual([{"id": "23b7b999-0a30-4b48-ae8f-ee201a88a6ab"}],
                         group.security_groups)
        self.assertEqual([{"id": "2daf6ba6-fb24-424a-b5b8-c554fab95f15"}],
                         group.networks)
        self.assertEqual("NOVA_AUDIT", group.health_periodic_audit_method)
        self.assertEqual(60, group.health_periodic_audit_time)
        self.assertEqual("OLD_CONFIG_OLD_INSTANCE",
                         group.instance_terminate_policy)
        self.assertEqual(True, group.is_scaling)
        self.assertEqual(False, group.delete_publicip)
        self.assertEqual(["EMAIL"], group.notifications)

    def test_delete_group_with_id(self):
        self.proxy.delete_group("some-group-id")
        self.assert_session_delete("scaling_group/some-group-id")

    def test_delete_group_with_instance(self):
        self.proxy.delete_group(_group.Group(id="some-group-id"))
        self.assert_session_delete("scaling_group/some-group-id")

    def test_resume_group(self):
        self.proxy.resume_group("some-group-id")
        uri = "scaling_group/some-group-id/action"
        self.assert_session_post_with(uri, json={"action": "resume"})

    def test_pause_group(self):
        self.proxy.pause_group("some-group-id")
        uri = "scaling_group/some-group-id/action"
        self.assert_session_post_with(uri, json={"action": "pause"})

    def test_update_group(self):
        self.mock_response_json_values({
            "scaling_group_id": "a8327883-6b07-4497-9c61-68d03ee193a1"
        })
        attrs = {
            "name": "group_1",
            "scaling_configuration_id":
                "f8327883-6a07-4497-9a61-68c03e8e72a2",
            "desire_instance_number": 1,
            "min_instance_number": 1,
            "max_instance_number": 3,
            "cool_down_time": 200
        }
        self.proxy.update_group("some-group-id", **attrs)
        expected_json = {
            "scaling_group_name": "group_1",
            "scaling_configuration_id":
                "f8327883-6a07-4497-9a61-68c03e8e72a2",
            "desire_instance_number": 1,
            "min_instance_number": 1,
            "max_instance_number": 3,
            "cool_down_time": 200
        }
        self.assert_session_put_with("scaling_group/some-group-id",
                                     json=expected_json)


class TestAutoScalingPolicy(TestAutoScalingProxy):
    def __init__(self, *args, **kwargs):
        super(TestAutoScalingPolicy, self).__init__(*args, **kwargs)

    def test_list_policy(self):
        query = {
            "name": "as-config-id",
            "type": "ALARM",
            "marker": 1
        }
        self.mock_response_json_file_values("list_policy.json")
        policies = list(self.proxy.policies("group-id", **query))

        transferred_query = {
            "scaling_group_id": "group-id",
            "scaling_policy_name": "as-config-id",
            "scaling_policy_type": "ALARM",
            "start_number": 1
        }
        self.assert_session_list_with("/scaling_policy/group-id/list",
                                      params=transferred_query)

        self.assertEqual(1, len(policies))

        policy = policies[0]
        self.verify_policy(policy)

    def verify_policy(self, policy1):
        self.assertIsInstance(policy1, _policy.Policy)
        self.assertEqual("fd7d63ce-8f5c-443e-b9a0-bef9386b23b3",
                         policy1.id)
        self.assertEqual("schedule1", policy1.name)
        self.assertEqual("INSERVICE", policy1.status)
        self.assertEqual("2015-07-24T01:09:30Z", policy1.create_time)
        self.assertEqual("2015-07-24T01:09:30Z", policy1.create_time)
        self.assertEqual("SCHEDULED", policy1.type)
        self.assertEqual(300, policy1.cool_down_time)
        self.assertEqual(_policy.ScheduledPolicy(**{
            "launch_time": "2015-07-24T01:21Z"
        }), policy1.scheduled_policy)
        self.assertEqual(_policy.Action(**{
            "operation": "REMOVE",
            "instance_number": 1
        }), policy1.scaling_policy_action)

    def test_create_policy(self):
        self.mock_response_json_values({
            "scaling_policy_id": "0h327883-324n-4dzd-9c61-68d03ee191dd"
        })
        attrs = self.get_file_content("create_policy.json")
        policy = self.proxy.create_policy(**attrs)
        expect_post_json = {
            "scaling_policy_name": "as-policy-7a75",
            "scaling_policy_action": {
                "operation": "ADD",
                "instance_number": 1
            },
            "cool_down_time": 900,
            "scheduled_policy": {
                "launch_time": "16:00",
                "recurrence_type": "Daily",
                "recurrence_value": None,
                "start_time": "2015-12-14T03:34Z",
                "end_time": "2015-12-27T03:34Z"
            },
            "scaling_policy_type": "RECURRENCE",
            "scaling_group_id": "5bc3aa02-b83e-454c-aba1-4d2095c68f8b"
        }

        self.assert_session_post_with("/scaling_policy",
                                      json=expect_post_json)
        self.assertEqual("0h327883-324n-4dzd-9c61-68d03ee191dd", policy.id)

    def test_get_policy_with_id(self):
        self.mock_response_json_file_values("get_policy.json")
        policy = self.proxy.get_policy("some-policy-id")
        self.session.get.assert_called_once_with(
            "scaling_policy/some-policy-id",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )
        self.verify_policy(policy)

    def test_delete_policy_with_id(self):
        self.proxy.delete_policy("some-policy-id")
        self.assert_session_delete("scaling_policy/some-policy-id")

    def test_delete_policy_with_instance(self):
        self.proxy.delete_policy(_policy.Policy(id="some-policy-id"))
        self.assert_session_delete("scaling_policy/some-policy-id")

    def test_resume_policy(self):
        self.proxy.resume_policy("some-policy-id")
        uri = "scaling_policy/some-policy-id/action"
        self.assert_session_post_with(uri, json={"action": "resume"})

    def test_pause_policy(self):
        self.proxy.pause_policy("some-policy-id")
        uri = "scaling_policy/some-policy-id/action"
        self.assert_session_post_with(uri, json={"action": "pause"})

    def test_execute_policy(self):
        self.proxy.execute_policy("some-policy-id")
        uri = "scaling_policy/some-policy-id/action"
        self.assert_session_post_with(uri, json={"action": "execute"})

    def test_update_policy(self):
        self.mock_response_json_values({
            "scaling_policy_id": "0h327883-324n-4dzd-9c61-68d03ee191dd"
        })
        attrs = {
            "scaling_policy_type": "RECURRENCE",
            "scaling_policy_name": "policy_01",
            "scheduled_policy": {
                "launch_time": "16:00",
                "recurrence_type": "Daily",
                "recurrence_value": None,
                "end_time": "2016-02-08T17:31Z",
                "start_time": "2016-01-08T17:31Z"
            },
            "scaling_policy_action": {
                "operation": "SET",
                "instance_number": 2
            },
            "cool_down_time": 300
        }

        self.proxy.update_policy("some-policy-id", **attrs)
        expected_json = {
            "scaling_policy_type": "RECURRENCE",
            "scaling_policy_name": "policy_01",
            "scheduled_policy": {
                "launch_time": "16:00",
                "recurrence_type": "Daily",
                "recurrence_value": None,
                "end_time": "2016-02-08T17:31Z",
                "start_time": "2016-01-08T17:31Z"
            },
            "scaling_policy_action": {
                "operation": "SET",
                "instance_number": 2
            },
            "cool_down_time": 300
        }
        self.assert_session_put_with("scaling_policy/some-policy-id",
                                     json=expected_json)


class TestAutoScalingInstance(TestAutoScalingProxy):
    def __init__(self, *args, **kwargs):
        super(TestAutoScalingInstance, self).__init__(*args, **kwargs)

    def test_remove_instance_with_instance(self):
        self.proxy.remove_instance(
            _instance.Instance(id="some-instance-id"))
        self.assert_session_delete(
            "scaling_group_instance/some-instance-id",
            params={"instance_delete": "no"})

    def test_remove_instance_with_id(self):
        self.proxy.remove_instance("some-instance-id")
        self.assert_session_delete(
            "scaling_group_instance/some-instance-id",
            params={"instance_delete": "no"})

    def test_delete_instance_with_instance(self):
        self.proxy.remove_instance(
            _instance.Instance(id="some-instance-id"),
            delete_instance=True)
        self.assert_session_delete(
            "scaling_group_instance/some-instance-id",
            params={"instance_delete": "yes"})

    def test_delete_instance_with_id(self):
        self.proxy.remove_instance("some-instance-id",
                                   delete_instance=True)
        self.assert_session_delete(
            "scaling_group_instance/some-instance-id",
            params={"instance_delete": "yes"})

    def test_batch_add_instances(self):
        instances = [
            "instance-id-1",
            "instance-id-2",
            _instance.Instance(id="instance-id-3")
        ]
        self.proxy.batch_add_instances("group-id", instances)
        self.assert_session_post_with(
            "scaling_group_instance/group-id/action",
            headers={"Accept": "*"},
            json={
                "action": "ADD",
                "instances_id": [
                    "instance-id-1",
                    "instance-id-2",
                    "instance-id-3"
                ]
            })

    def test_batch_remove_instance(self):
        instances = [
            "instance-id-1",
            "instance-id-2",
            _instance.Instance(id="instance-id-3")
        ]
        self.proxy.batch_remove_instances("group-id", instances)
        self.assert_session_post_with(
            "scaling_group_instance/group-id/action",
            headers={"Accept": "*"},
            json={
                "action": "REMOVE",
                "instances_id": [
                    "instance-id-1",
                    "instance-id-2",
                    "instance-id-3"
                ],
                "instance_delete": "no"
            })

    def test_batch_remove_and_delete_instance(self):
        instances = [
            "instance-id-1",
            "instance-id-2",
            _instance.Instance(id="instance-id-3")
        ]
        self.proxy.batch_remove_instances("group-id",
                                          instances,
                                          delete_instance=True)
        self.assert_session_post_with(
            "scaling_group_instance/group-id/action",
            headers={"Accept": "*"},
            json={
                "action": "REMOVE",
                "instances_id": [
                    "instance-id-1",
                    "instance-id-2",
                    "instance-id-3"
                ],
                "instance_delete": "yes"
            })

    def test_list_instance(self):
        query = {
            "health_status": "INITIALIZING",
            "lifecycle_status": "PENDING",
            "marker": 1
        }
        self.mock_response_json_file_values("list_instance.json")
        instances = list(self.proxy.instances("group-id", **query))

        transferred_query = {
            "scaling_group_id": "group-id",
            "health_status": "INITIALIZING",
            "life_cycle_state": "PENDING",
            "start_number": 1
        }
        self.assert_session_list_with(
            "/scaling_group_instance/group-id/list",
            params=transferred_query)
        self.assertEqual(1, len(instances))
        instance = instances[0]
        self.assertIsInstance(instance, _instance.Instance)
        self.assertEqual("b25c1589-c96c-465b-9fef-d06540d1945c",
                         instance.id)
        self.assertEqual("e5d27f5c-dd76-4a61-b4bc-a67c5686719a",
                         instance.scaling_group_id)
        self.assertEqual("discuz_3D210808", instance.name)
        self.assertEqual("INSERVICE", instance.lifecycle_state)
        self.assertEqual("NORMAL", instance.health_status)
        self.assertEqual("discuz", instance.scaling_configuration_name)
        self.assertEqual("ca3dcd84-d197-4c4f-af2a-cf8ba39696ac",
                         instance.scaling_configuration_id)
        self.assertEqual("2015-07-23T06:47:33Z", instance.create_time)


class TestAutoScalingActivity(TestAutoScalingProxy):
    def __init__(self, *args, **kwargs):
        super(TestAutoScalingActivity, self).__init__(*args, **kwargs)

    def test_list_activities(self):
        query = {
            "start_time": "2015-07-24T01:21:02Z",
            "end_time": "2015-07-25T01:21:02Z",
            "marker": 0
        }
        self.mock_response_json_file_values("list_activities.json")
        activities = list(self.proxy.activities("any-group-id", **query))

        transferred_query = {
            "start_time": "2015-07-24T01:21:02Z",
            "end_time": "2015-07-25T01:21:02Z",
            "scaling_group_id": "any-group-id",
            "start_number": 0
        }
        self.assert_session_list_with("/scaling_activity_log/any-group-id",
                                      params=transferred_query)

        self.assertEqual(2, len(activities))

        activity = activities[0]
        self.assertIsInstance(activity, _activity_log.Activity)
        self.assertEqual("a8924393-1024-4c24-8ac6-e4d481360884",
                         activity.id)
        self.assertEqual("SUCCESS", activity.status)
        self.assertEqual(1, activity.instance_value)
        self.assertEqual(0, activity.desire_value)
        self.assertEqual("2015-07-24T01:21:02Z", activity.start_time)
        self.assertEqual("2015-07-24T01:23:31Z", activity.end_time)
        self.assertEqual("as-config-TEO_XQF2JJSI",
                         activity.instance_added_list)


class TestAutoScalingQuota(TestAutoScalingProxy):
    def __init__(self, *args, **kwargs):
        super(TestAutoScalingQuota, self).__init__(*args, **kwargs)

    def test_list_quota(self):
        self.mock_response_json_file_values("list_quota.json")
        quotas = list(self.proxy.quotas())
        self.assert_session_list_with("/quotas")
        self.assertEqual(4, len(quotas))

        quota = quotas[0]
        self.assertIsInstance(quota, _quota.Quota)
        self.assertEqual("scaling_Group", quota.type)
        self.assertEqual(2, quota.used)
        self.assertEqual(25, quota.quota)
        self.assertEqual(50, quota.max)

    def test_list_scaling_quota(self):
        self.mock_response_json_file_values("list_scaling_quota.json")
        quotas = list(self.proxy.quotas("group-id"))
        self.assert_session_list_with("/quotas/group-id",
                                      params={
                                          "scaling_group_id": "group-id"})
        self.assertEqual(2, len(quotas))

        quota = quotas[0]
        self.assertIsInstance(quota, _quota.Quota)
        self.assertEqual("scaling_Policy", quota.type)
        self.assertEqual(2, quota.used)
        self.assertEqual(50, quota.quota)
        self.assertEqual(50, quota.max)
