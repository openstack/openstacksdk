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

'''
List resources from the Load Balancer service.

For a full guide see TODO(etoews):link to docs on developer.openstack.org
'''


# import sys

# from openstack import utils


def list_loadbalancers(conn):
    print('List Load Balancer:')
    query = {
        # 'vip_address': '192.168.2.36'
        # 'name': 'elb-yc5f'
    }
    for load_balancer in conn.load_balancer.load_balancers(**query):
        print(load_balancer)


def create_load_balancer(conn):
    lb = {
        'name': 'elb-python-sdk-1',
        'type': 'Internal',
        'bandwidth': 200,
        'availability_zone': 'eu-de',
        'security_group_id': '0005ba27-b937-4a7c-a280-c7b65cea2e47',
        'vpc_id': '31d158b8-e7d7-4b4a-b2a7-a5240296b267',
        'vip_subnet_id': 'cb9a6ede-39c6-498f-ad85-c554ef7220fc',
        'vip_address': '192.168.2.36',
        'admin_state_up': 0,
        'description': 'elb-python-sdk-1 description'
    }
    conn.load_balancer.create_load_balancer(**lb)


def get_load_balancer(conn):
    conn.load_balancer.get_load_balancer('lb_id')


def delete_load_balancer(conn):
    conn.load_balancer.delete_load_balancer('lb_id')
