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
Delete resources from the DNS service.

For a full guide see
https://docs.openstack.org/openstacksdk/latest/user/guides/dns.html
"""


def delete_zone(conn, name_or_id):
    print(f"Delete Zone: {name_or_id}")

    zone = conn.dns.find_zone(name_or_id)

    if zone:
        conn.dns.delete_zone(zone.id)
    else:
        return None


def delete_recordset(conn, name_or_id, recordset_name):
    print(f"Deleting Recordset: {recordset_name} in Zone: {name_or_id}")

    zone = conn.dns.find_zone(name_or_id)

    if zone:
        try:
            recordset = conn.dns.find_recordset(zone.id, recordset_name)
            if recordset:
                conn.dns.delete_recordset(recordset, zone.id)
            else:
                print("Recordset not found")
        except Exception as e:
            print(f"{e}")
    else:
        return None
