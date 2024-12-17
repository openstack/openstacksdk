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
Find resources from the DNS service.

For a full guide see
https://docs.openstack.org/openstacksdk/latest/user/guides/dns.html
"""


def find_zone(conn, name_or_id):
    print(f"Find Zone: {name_or_id}")

    zone = conn.dns.find_zone(name_or_id)

    if zone:
        print(zone)
        return zone
    else:
        print("Zone not found.")
        return None


def find_recordset(conn, name_or_id, recordset_name, recordset_type=None):
    print(f"Find Recordset: {recordset_name} in Zone: {name_or_id}")

    zone = conn.dns.find_zone(name_or_id)

    if not zone:
        print("Zone not found.")
        return None

    zone_id = zone.id

    try:
        if recordset_type:
            recordset = conn.dns.find_recordset(
                zone_id, recordset_name, type=recordset_type
            )
        else:
            recordset = conn.dns.find_recordset(zone_id, recordset_name)

        if recordset:
            print(recordset)
            return recordset
        else:
            print("Recordset not found in Zone.")
            return None

    except Exception as e:
        print(f"{e}")
        return None
