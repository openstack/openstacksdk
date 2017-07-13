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


def list_groups(conn):
    query = {
        "name": "any-as-group-name",
        "status": "INSERVICE",  # INSERVICE，PAUSED，ERROR
        "scaling_configuration_id": "as-config-id",
        "marker": 0,
        "limit": 20
    }
    groups = conn.auto_scaling.groups(**query)
    for group in groups:
        logging.info(group)


def get_group(conn):
    group_id = "some-group-id"
    group = conn.auto_scaling.get_group(group_id)
    logging.info(group)


def create_group(conn):
    flavor_id = ""
    image_id = ""
    key_name = ""
    _group = {
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
    group = conn.auto_scaling.create_group("some-group-name",
                                           **_group)
    logging.info(group)


def delete_group(conn):
    group_id = "some-group-id"
    conn.auto_scaling.delete_group(group_id)


def batch_delete_group(conn):
    ids = ["group-id-1", "group-id-2"]
    conn.auto_scaling.batch_delete_groups(ids)
