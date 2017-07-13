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


def list_ptrs(conn):
    query = {
        'limit': 10
    }
    for ptr in conn.dns.ptrs(**query):
        logging.info(ptr)


def create_ptr(conn):
    ptr = {
        'ptrdname': 'www.turnbig.net',
        'description': 'HaveFun.lee - For Test',
        'ttl': 300,
        'region': 'eu-de',
        'floating_ip_id': '9e9c6d33-51a6-4f84-b504-c13301f1cc8c'
    }
    ptr = conn.dns.create_ptr(**ptr)
    logging.info(ptr)
    return ptr


def get_ptr(conn):
    ptr = conn.dns.get_ptr('eu-de', '9e9c6d33-51a6-4f84-b504-c13301f1cc8c')
    logging.info(ptr)


def restore_ptr(conn):
    conn.dns.restore_ptr('eu-de', '9e9c6d33-51a6-4f84-b504-c13301f1cc8c')

# list_ptrs(connection)
# get_ptr(connection)
# create_ptr(connection)
# restore_ptr(connection)
