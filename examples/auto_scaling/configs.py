# Copyright 2017 HuaWei Tld
# Copyright 2017 OpenStack.org
#
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

import logging

from openstack import utils


def list_configs(conn):
    query = {
        "name": "config-name",
        "image_id": "some-image-id",
        "limit": 10,
        "marker": 20
    }
    for config in conn.auto_scaling.configs(**query):
        logging.info(config)


def get_config(conn):
    config_id = "some-config-id"
    config = conn.auto_scaling.get_config(config_id)
    logging.info(config)


def create_config(conn):
    flavor_id = ""
    image_id = ""
    key_name = ""
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
    config = conn.auto_scaling.create_config("some-config-name",
                                             **_config)
    logging.info(config)


def delete_config(conn):
    config_id = "some-config-id"
    conn.auto_scaling.delete_config(config_id)


def batch_delete_config(conn):
    ids = ["config-id-1", "config-id-2"]
    conn.auto_scaling.batch_delete_configs(ids)
