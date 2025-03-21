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

"""
List resources from the DNS service.

For a full guide see
https://docs.openstack.org/openstacksdk/latest/user/guides/dns.html
"""


def list_zones(conn):
    print("List Zones:")

    for zone in conn.dns.zones():
        print(zone)


def list_recordsets(conn, name_or_id):
    print("List Recordsets for Zone")

    zone = conn.dns.find_zone(name_or_id)

    if zone:
        zone_id = zone.id
        recordsets = conn.dns.recordsets(zone_id)

        for recordset in recordsets:
            print(recordset)
    else:
        print("Zone not found.")
