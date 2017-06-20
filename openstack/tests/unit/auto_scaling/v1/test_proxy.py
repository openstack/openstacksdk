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

import datetime

import mock

from openstack import utils
from openstack.auto_scaling import auto_scaling_service
from openstack.auto_scaling.v1 import _proxy
from openstack.auto_scaling.v1 import config as _config
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
            "marker": 0,
            "limit": 20
        }
        self.mock_response_json_file_values("list_config.json")
        configs = list(self.proxy.configs(**query))

        transferred_query = {
            "scaling_configuration_name": "as_config_name",
            "image_id": "image-ref-id",
            "start_number": 0,
            "limit": 20
        }
        self.assert_session_get_with("/scaling_configuration",
                                     params=transferred_query)

        self.assertEquals(2, len(configs))

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
        self.assertEqual([{"size": 40,
                           "volume_type": "SATA",
                           "disk_type": "SYS"
                           }, {
                              "size": 100,
                              "volume_type": "SATA",
                              "disk_type": "DATA"
                          }], instance_config.disk)

    def test_create_config(self):
        self.mock_response_json_values({
            "scaling_configuration_id":
                "f8327883-6a07-4497-9a61-68c03e8e72a2"
        })

        instance_config = {
            "flavor_id": "103",
            "image_id": "627a1223-2ca3-46a7-8d5f-7aef22c74ee6",
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

        config = self.proxy.create_config("as_config_name", **instance_config)
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
        self.assertEquals("6afe46f9-7d3d-4046-8748-3b2a1085ad86", config.id)
        self.assertEquals("config_name_1", config.name)
        self.assertEquals("2015-07-23T01:04:07Z", config.create_time)
        self.assertIsInstance(config.instance_config, _config.InstanceConfig)
        ic = config.instance_config
        self.assertEquals("37ca2b35-6fc7-47ab-93c7-900324809c5c", ic.image_id)
        self.assertEquals("103", ic.flavor_id)
        self.assertEquals("keypair01", ic.key_name)
        self.assertEquals([{"size": 40,
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
