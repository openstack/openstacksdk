#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
import uuid

from openstack.tests.functional import base
from openstack import utils


def auto_create_config(conn, config_name):
    flavor = conn.compute.find_flavor(base.FLAVOR_NAME,
                                      ignore_missing=False)
    image = conn.compute.find_image(base.IMAGE_NAME,
                                    ignore_missing=False)
    keypairs = list(conn.compute.keypairs())
    if len(keypairs) == 0:
        raise Exception("no keypair available for test")
    return create_config(conn,
                         config_name,
                         flavor.id,
                         image.id,
                         keypairs[0].name)


def create_config(conn, name, flavor_id, image_id, key_name):
    _config = {
        "flavor_id": flavor_id,
        "image_id": image_id,
        "disk": [{
            "size": 40,
            "volume_type": "SATA",
            "disk_type": "SYS"
        }],
        "personality": [{
            "path": "/etc/p1.txt",
            "content": utils.b64encode("p1")
        }, {
            "path": "/etc/p2.txt",
            "content": utils.b64encode("p2")
        }],
        "metadata": {
            "tag": "app",
            "node": "node2"
        },
        "key_name": key_name
    }
    return conn.auto_scaling.create_config(name, **_config)


class TestConfig(base.BaseFunctionalTest):
    CONFIG_NAME = "SDK-" + uuid.uuid4().hex
    config = None

    @classmethod
    def setUpClass(cls):
        super(TestConfig, cls).setUpClass()
        cls.config = auto_create_config(cls.conn, cls.CONFIG_NAME)

    @classmethod
    def tearDownClass(cls):
        cls.conn.auto_scaling.delete_config(cls.config)

    def test_list_config(self):
        configs = list(self.conn.auto_scaling.configs(name=self.CONFIG_NAME))
        self.assertEqual(1, len(list(configs)))
        self.assertEqual(self.config.id, configs[0].id)

    def test_get_config(self):
        _config = self.conn.auto_scaling.get_config(self.config.id)
        self.assertEqual(_config.id, self.config.id)

    def test_batch_delete(self):
        configs = []
        for i in range(3):
            name = "SDK-" + uuid.uuid4().hex
            created = create_config(self.conn,
                                    name,
                                    self.config.instance_config.flavor_id,
                                    self.config.instance_config.image_id,
                                    self.config.instance_config.key_name)
            configs.append(created)
        self.conn.auto_scaling.batch_delete_configs(configs)

        _exists = self.conn.auto_scaling.configs(name=configs[0].name)
        self.assertEqual(0, len(list(_exists)))
