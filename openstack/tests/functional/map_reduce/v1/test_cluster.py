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


def auto_create_cluster(conn, name, router, subnet, keypair):
    # OTC ENV hard-code resources
    vpc_id = "31d158b8-e7d7-4b4a-b2a7-a5240296b267"
    vpc_name = "vpc-console-bosh"
    subnet_id = "cb9a6ede-39c6-498f-ad85-c554ef7220fc"
    subnet_name = "cf2"
    keypair_name = "KeyPair-28ice"

    cluster = {
        "cluster_name": name,
        "billing_type": 12,
        "data_center": "eu-de",
        "master_node_num": 2,
        "master_node_size": "c2.4xlarge.linux.mrs",
        "core_node_num": 3,
        "core_node_size": "s1.xlarge.linux.mrs",
        "available_zone_id": "eu-de-01",
        "vpc": vpc_name,
        "vpc_id": vpc_id,
        "subnet_id": subnet_id,
        "subnet_name": subnet_name,
        "cluster_version": "MRS 1.3.0",
        "cluster_type": 0,
        "volume_type": "SSD",
        "volume_size": 100,
        "keypair": keypair_name,
        "safe_mode": 0,
        "component_list": [{
            "component_id": "MRS 1.3.0_001",
            "component_name": "Hadoop"
        }]
    }

    job = {
        "job_type": 1,
        "job_name": "SDK-MapReduce",
        "jar_path": "s3a://sdk-unittest/hadoop-mapreduce-examples-2.7.2.jar",
        "arguments": "wordcount",
        "input": "s3a://sdk-unittest/input",
        "output": "s3a://sdk-unittest/ouput",
        "job_log": "s3a://sdk-unittest/log/",
        "shutdown_cluster": False,
        "file_action": "",
        "submit_job_once_cluster_run": False,
        "hql": "",
        "hive_script_path": ""
    }
    return conn.map_reduce.create_cluster_and_run_job(cluster, job)


class TestCluster(base.BaseFunctionalTest):
    NAME = "SDK-" + uuid.uuid4().hex
    cluster = None

    @classmethod
    def setUpClass(cls):
        super(TestCluster, cls).setUpClass()
        # router = cls.get_first_router()
        # subnet = cls.get_first_subnet()
        # keypair = cls.get_first_keypair()
        cls.cluster = auto_create_cluster(cls.conn,
                                          cls.NAME,
                                          cls.router,
                                          cls.subnet,
                                          cls.keypair)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_1_get_cluster(self):
        self.cluster = self.conn.map_reduce.get_cluster(self.cluster.id)
