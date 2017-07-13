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

from openstack.dns.v2.zone import Zone


def list_zones(conn):
    query = {
        # 'vip_address': '192.168.2.36'
        'type': 'private',
        'limit': 3
    }
    for zone in conn.dns.zones(**query):
        logging.info(zone)


def create_zone(conn):
    zone = {
        'name': 'turnbig.net',
        'description': 'This is an example zone.',
        'zone_type': 'private',
        'email': 'admin@turnbig.net',
        'ttl': 500,
        'router': {
            'router_id': '5fbf2de5-c7e5-4ec5-92ef-1e0b128f729f',
            'router_region': 'eu-de'
        }
    }
    zone = conn.dns.create_zone(**zone)
    logging.info(zone)
    return zone


def get_zone(conn, zone_id):
    zone = conn.dns.get_zone(zone_id)
    logging.info(zone)

    zone = conn.dns.get_zone(Zone(id=zone_id))
    logging.info(zone)


def delete_zone(conn):
    conn.dns.delete_backup('ff8080825ca5c454015ca6eefb480067')


def get_nameservers(conn):
    # zone = create_zone(conn)
    nameservers = conn.dns.nameservers(
        'ff8080825ca865e8015ca99563af004a'
    )

    for nameserver in nameservers:
        logging.info(nameserver)


def add_router_to_zone(conn):
    router = {
        'router_id': '62615060-5a38-42d4-a391-9b8a109da548',
        'router_region': 'eu-de'
    }
    conn.dns.add_router_to_zone('ff8080825ca865e8015ca99563af004a', **router)


def remove_router_from_zone(conn):
    router = {
        'router_id': '62615060-5a38-42d4-a391-9b8a109da548',
        'router_region': 'eu-de'
    }
    result = conn.dns.remove_router_from_zone(
        'ff8080825ca865e8015ca99563af004a',
        **router
    )

    logging.info(result)
