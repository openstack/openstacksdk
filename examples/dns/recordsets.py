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

from openstack.dns.v2.recordset import Recordset
from openstack.dns.v2.zone import Zone


def list_recordsets(conn):
    query = {
        'limit': 5
    }
    zone_id = 'ff8080825ca865e8015caa9f452700a8'
    recordsets = conn.dns.recordsets(zone_id, **query)
    for recordset in recordsets:
        logging.info(recordset)


def create_recordset(conn):
    recordset = {
        "name": "api.turnbig.net",
        "description": "This is an example record set.",
        "type": "CNAME",
        "ttl": 3600,
        "records": [
            "www.turnbig.net"
        ]
    }

    recordset = conn.dns.create_recordset('ff8080825ca865e8015caa9f452700a8',
                                          **recordset)
    logging.info(recordset)
    return recordset


def get_recordset(conn, recordset_id):
    zone = Zone(id='ff8080825ca865e8015caa9f452700a8')
    recordset = conn.dns.get_recordset(zone, recordset_id)
    recordset = conn.dns.get_recordset(zone, Recordset(id=recordset_id))
    recordset = conn.dns.get_recordset(zone.id, recordset_id)
    recordset = conn.dns.get_recordset(zone.id, Recordset(id=recordset_id))
    logging.info(recordset)


def delete_recordset(conn):
    zone = Zone(id='ff8080825ca865e8015caa9f452700a8')
    recordset = Recordset(id='ff8080825ca865e8015caaaa0e1500ba')
    conn.dns.delete_recordset(zone, recordset)


def all_recordsets(conn):
    query = {
        'limit': 100
    }
    recordsets = conn.dns.all_recordsets(**query)
    for recordset in recordsets:
        logging.info(recordset)
