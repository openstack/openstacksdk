class TestAutoScalingDataSource(TestAutoScalingProxy):
    def __init__(self, *args, **kwargs):
        super(TestAutoScalingDataSource, self).__init__(*args, **kwargs)

    def test_list_data_source(self):
        query = {
            "name": "as_data_source_name",
            "image_id": "image-ref-id",
            "marker": 0
        }
        self.mock_response_json_file_values("list_ds.json")
        configs = list(self.proxy.configs(**query))

        transferred_query = {
            "scaling_data_sourceuration_name": "as_data_source_name",
            "image_id": "image-ref-id",
            "start_number": 0
        }
        self.assert_session_list_with("/scaling_data_sourceuration",
                                      params=transferred_query)

        self.assertEquals(2, len(configs))

        config1 = configs[0]
        self.assertIsInstance(config1, _ds.DataSource)
        self.assertEqual("6afe46f9-7d3d-4046-8748-3b2a1085ad86",
                         config1.id)
        self.assertEqual("config_name_1", config1.name)
        self.assertEqual("STANDBY", config1.status)
        self.assertEqual("2015-07-23T01:04:07Z", config1.create_time)

        instance_data_source = config1.instance_data_source
        self.assertIsNone(instance_ds.id)
        self.assertIsNone(instance_ds.name)
        self.assertEqual("103", instance_ds.flavor_id)
        self.assertEqual("37ca2b35-6fc7-47ab-93c7-900324809c5c",
                         instance_ds.image_id)
        self.assertEqual("keypair02", instance_ds.key_name)
        self.assertEqual([{"size": 40,
                           "volume_type": "SATA",
                           "disk_type": "SYS"
                           }, {
                              "size": 100,
                              "volume_type": "SATA",
                              "disk_type": "DATA"
                          }], instance_ds.disk)

    def test_create_data_source(self):
        self.mock_response_json_values({
            "scaling_data_sourceuration_id":
                "f8327883-6a07-4497-9a61-68c03e8e72a2"
        })

        instance_data_source = {
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

        config = self.proxy.create_data_source("as_data_source_name", **instance_data_source)
        expect_post_json = {
            "scaling_data_sourceuration_name": "as_data_source_name",
            "instance_data_source": {
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
        self.assert_session_post_with("/scaling_data_sourceuration",
                                      json=expect_post_json)
        self.assertEqual("f8327883-6a07-4497-9a61-68c03e8e72a2", config.id)

    def test_get_data_source_with_id(self):
        self.mock_response_json_file_values("get_ds.json")
        config = self.proxy.get_data_source("some-config-id")
        self.session.get.assert_called_once_with(
            "scaling_data_sourceuration/some-config-id",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )
        self.assertIsInstance(config, _ds.DataSource)
        self.assertEquals("6afe46f9-7d3d-4046-8748-3b2a1085ad86", config.id)
        self.assertEquals("config_name_1", config.name)
        self.assertEquals("2015-07-23T01:04:07Z", config.create_time)
        self.assertIsInstance(config.instance_data_source, _ds.InstanceDataSource)
        ic = config.instance_data_source
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

    def test_delete_data_source_with_id(self):
        self.proxy.delete_data_source("some-config-id")
        self.assert_session_delete("scaling_data_sourceuration/some-config-id")

    def test_delete_data_source_with_instance(self):
        self.proxy.delete_data_source(_ds.DataSource(id="some-config-id"))
        self.assert_session_delete("scaling_data_sourceuration/some-config-id")

    def test_batch_delete_data_sources(self):
        configs = [
            "config-id-1",
            "config-id-2",
            _ds.DataSource(id="config-id-3")
        ]
        self.proxy.batch_delete_data_sources(configs)
        self.assert_session_post_with("/scaling_data_sourceurations",
                                      headers={"Accept": "*"},
                                      json={
                                          "scaling_data_sourceuration_id": [
                                              "config-id-1",
                                              "config-id-2",
                                              "config-id-3"
                                          ]
                                      })