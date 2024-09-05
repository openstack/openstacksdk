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
Create resources from the DNS service.

For a full guide see
https://docs.openstack.org/openstacksdk/latest/user/guides/dns.html
"""


def create_zone(
    conn,
    name,
    email,
    ttl=3600,
    description="Default description",
    zone_type="PRIMARY",
):
    print("Create Zone: ")

    zone = {
        "name": name,
        "email": email,
        "ttl": ttl,
        "description": description,
        "type": zone_type,
    }

    print(conn.dns.create_zone(**zone))


def create_recordset(
    conn,
    name_or_id,
    recordset_name,
    recordset_type="A",
    records=["192.168.1.1"],
    ttl=3600,
    description="Default description",
):
    print("Create Recordset: ")

    zone = conn.dns.find_zone(name_or_id)

    if not zone:
        print("Zone not found.")
        return None

    zone_id = zone.id

    recordset_data = {
        "name": recordset_name,
        "type": recordset_type,
        "records": records,
        "ttl": ttl,
        "description": description,
    }

    print(conn.dns.create_recordset(zone_id, **recordset_data))
