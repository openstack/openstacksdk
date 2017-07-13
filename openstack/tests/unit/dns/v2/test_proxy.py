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

from openstack.dns import dns_service
from openstack.dns.v2 import _proxy
from openstack.dns.v2 import ptr as _ptr
from openstack.dns.v2 import recordset as _recordset
from openstack.dns.v2 import zone as _zone
from openstack.tests.unit.test_proxy_base3 import BaseProxyTestCase


class TestDNSProxy(BaseProxyTestCase):
    def __init__(self, *args, **kwargs):
        super(TestDNSProxy, self).__init__(
            *args,
            proxy_class=_proxy.Proxy,
            service_class=dns_service.DNSService,
            **kwargs)


class TestZone(TestDNSProxy):
    def test_list_zones(self):
        query = {
            'zone_type': 'public',
            'limit': 10
        }
        self.mock_response_json_file_values('list_zone.json')
        zones = list(self.proxy.zones(**query))
        self.assert_session_list_with('/zones', query)
        self.assertEqual(2, len(zones))
        zone = zones[0]
        self.assertEqual(zone.id, '2c9eb155587194ec01587224c9f90149')
        self.assertEqual(zone.name, 'example.com.')
        self.assertEqual(zone.description, "This is an example zone.")
        self.assertEqual(zone.email, "xx@example.com")
        self.assertEqual(zone.ttl, 300)
        self.assertEqual(zone.serial, 0)
        self.assertEqual(zone.masters, [])
        self.assertEqual(zone.status, "ACTIVE")
        self.assertEqual(zone.pool_id, "00000000570e54ee01570e9939b20019")
        self.assertEqual(zone.zone_type, "public")
        self.assertEqual(zone.created_at, "2016-11-17T11:56:03.439")
        self.assertEqual(zone.record_num, 2)

    def test_create_public_zone(self):
        attrs = {
            "name": "example.com.",
            "description": "This is an example zone.",
            "zone_type": "public",
            "email": "xx@example.com"
        }
        self.mock_response_json_file_values('create_public_zone.json')
        zone = self.proxy.create_zone(**attrs)
        self.assert_session_post_with('/zones', json=attrs, headers={})
        self.assertEqual(zone.name, 'example.com.')
        self.assertEqual(zone.zone_type, 'public')
        self.assertEqual(zone.email, 'xx@example.com')
        self.assertIsNotNone(zone.id)

    def test_create_private_zone(self):
        attrs = {
            "name": "example.com.",
            "description": "This is an example zone.",
            "zone_type": "private",
            "email": "xx@example.org",
            "router": {
                "router_id": "19664294-0bf6-4271-ad3a-94b8c79c6558",
                "router_region": "eu-de"
            }
        }

        self.mock_response_json_file_values('create_private_zone.json')
        zone = self.proxy.create_zone(**attrs)
        self.assert_session_post_with('/zones', json=attrs, headers={})
        self.assertEqual(zone.name, 'example.com.')
        self.assertEqual(zone.zone_type, 'private')
        self.assertEqual(zone.email, 'xx@example.com')
        self.assertIsNotNone(zone.router)
        self.assertEqual(zone.router.router_id,
                         "19664294-0bf6-4271-ad3a-94b8c79c6558")
        self.assertEqual(zone.router.router_region, "eu-de")
        self.assertIsNotNone(zone.id)

    def test_get_zone_with_id(self):
        self.mock_response_json_file_values("get_zone_response.json")
        zone = self.proxy.get_zone("zone-id")
        self.session.get.assert_called_once_with(
            "zones/zone-id",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )

        self.assertIsInstance(zone, _zone.Zone)
        self.assertEqual("2c9eb155587194ec01587224c9f90149", zone.id)
        self.assertEqual("example.com.", zone.name)
        self.assertEqual("This is an example zone.", zone.description)
        self.assertEqual("xx@example.com", zone.email)
        self.assertEqual(300, zone.ttl)
        self.assertEqual(0, zone.serial)
        self.assertEqual([], zone.masters)
        self.assertEqual("ACTIVE", zone.status)
        self.assertEqual("00000000570e54ee01570e9939b20019", zone.pool_id)
        self.assertEqual("e55c6f3dc4e34c9f86353b664ae0e70c", zone.project_id)
        self.assertEqual("public", zone.zone_type)
        self.assertEqual("2016-11-17T11:56:03.439", zone.created_at)
        self.assertEqual(2, zone.record_num)

    def test_delete_zone_with_id(self):
        self.proxy.delete_zone("zone-id")
        self.assert_session_delete("zones/zone-id")

    def test_delete_zone_with_instance(self):
        self.proxy.delete_zone(_zone.Zone(id="zone-id"))
        self.assert_session_delete("zones/zone-id")

    def test_list_public_zone_nameservers(self):
        self.mock_response_json_file_values(
            "list_public_zone_ns_response.json")
        nameservers = list(self.proxy.nameservers("zone-id"))
        self.assert_session_list_with("/zones/zone-id/nameservers")
        self.assertEqual(2, len(nameservers))
        ns = nameservers[0]
        self.assertEqual("ns1.huawei.com.", ns.hostname)
        self.assertEqual(1, ns.priority)

    def test_list_private_zone_nameservers(self):
        self.mock_response_json_file_values(
            "list_private_zone_ns_response.json")
        nameservers = list(self.proxy.nameservers("zone-id"))
        self.assert_session_list_with("/zones/zone-id/nameservers")
        self.assertEqual(2, len(nameservers))
        ns = nameservers[0]
        self.assertEqual("100.125.0.81", ns.address)
        self.assertEqual(1, ns.priority)

    def test_add_router_to_zone(self):
        self.mock_response_json_values({
            "status": "PENDING_CREATE",
            "router_id": "f0791650-db8c-4a20-8a44-a06c6e24b15b",
            "router_region": "xx"
        })

        router = {
            "router_id": "f0791650-db8c-4a20-8a44-a06c6e24b15b",
            "router_region": "xx"
        }

        result = self.proxy.add_router_to_zone("zone-id", **router)
        self.assert_session_post_with("/zones/zone-id/associaterouter",
                                      dict(router=router))
        self.assertEqual("f0791650-db8c-4a20-8a44-a06c6e24b15b",
                         result.router_id)
        self.assertEqual("xx", result.router_region)
        self.assertEqual("PENDING_CREATE", result.status)

    def test_remove_router_from_zone(self):
        self.mock_response_json_values({
            "status": "PENDING_DELETE",
            "router_id": "f0791650-db8c-4a20-8a44-a06c6e24b15b",
            "router_region": "xx"
        })

        router = {
            "router_id": "f0791650-db8c-4a20-8a44-a06c6e24b15b",
            "router_region": "xx"
        }

        result = self.proxy.remove_router_from_zone("zone-id", **router)
        self.assert_session_post_with("/zones/zone-id/disassociaterouter",
                                      dict(router=router))
        self.assertEqual("f0791650-db8c-4a20-8a44-a06c6e24b15b",
                         result.router_id)
        self.assertEqual("xx", result.router_region)
        self.assertEqual("PENDING_DELETE", result.status)


class TestRecordset(TestDNSProxy):
    def __init__(self, *args, **kwargs):
        super(TestRecordset, self).__init__(*args, **kwargs)

    def test_create_recordset(self):
        self.mock_response_json_file_values(
            "create_recordset_response.json")

        data = {
            "name": "www.example.com.",
            "description": "This is an example record set.",
            "type": "A",
            "ttl": 3600,
            "records": [
                "192.168.10.1",
                "192.168.10.2"
            ]
        }

        recordset = self.proxy.create_recordset("zone-id", **data)
        self.assert_session_post_with("/zones/zone-id/recordsets",
                                      json=data)
        self.assertIsInstance(recordset, _recordset.Recordset)
        self.assertEqual("2c9eb155587228570158722b6ac30007", recordset.id)
        self.assertEqual("www.example.com.", recordset.name)
        self.assertEqual("This is an example record set.",
                         recordset.description)
        self.assertEqual("A", recordset.type)
        self.assertEqual(300, recordset.ttl)
        self.assertEqual(["192.168.10.1", "192.168.10.2"], recordset.records)
        self.assertEqual("PENDING_CREATE", recordset.status)
        self.assertEqual("zone-id", recordset.zone_id)
        self.assertEqual("example.com.", recordset.zone_name)
        self.assertEqual("2016-11-17T12:03:17.827", recordset.create_at)
        self.assertEqual("e55c6f3dc4e34c9f86353b664ae0e70c",
                         recordset.project_id)
        self.assertFalse(recordset.is_default)

    def test_list_recordset(self):
        query = {
            "limit": 20,
            "marker": "recordset-id"
        }
        self.mock_response_json_file_values("list_recordset_response.json")
        recordsets = list(self.proxy.recordsets("zone-id", **query))
        self.assert_session_list_with("/zones/zone-id/recordsets",
                                      params=query)
        self.assertEqual(5, len(recordsets))

        recordset = recordsets[0]
        self.verify_recordset(recordset)

    def test_list_all_recordset(self):
        query = {
            "limit": 20,
            "marker": "recordset-id"
        }
        self.mock_response_json_file_values("list_all_recordset_response.json")
        recordsets = list(self.proxy.all_recordsets(**query))
        self.assert_session_list_with("/recordsets", params=query)
        self.assertEqual(5, len(recordsets))

        recordset = recordsets[0]
        self.verify_recordset(recordset)

    def verify_recordset(self, recordset):
        self.assertIsInstance(recordset, _recordset.Recordset)
        self.assertEqual("2c9eb155587194ec01587224c9f9014a", recordset.id)
        self.assertEqual("example.com.", recordset.name)
        self.assertIsNone(recordset.description)
        self.assertEqual("SOA", recordset.type)
        self.assertEqual(300, recordset.ttl)
        self.assertEqual(
            ["ns1.hotrot.de. xx.example.com. (1 7200 900 1209600 300)"],
            recordset.records)
        self.assertEqual("ACTIVE", recordset.status)
        self.assertEqual("2c9eb155587194ec01587224c9f90149", recordset.zone_id)
        self.assertEqual("example.com.", recordset.zone_name)
        self.assertEqual("2016-11-17T11:56:03.439", recordset.create_at)
        self.assertEqual("e55c6f3dc4e34c9f86353b664ae0e70c",
                         recordset.project_id)
        self.assertTrue(recordset.is_default)

    def test_get_recordset_with_id(self):
        self.mock_response_json_file_values("get_recordset_response.json")
        recordset = self.proxy.get_recordset("zone-id", "recordset-id")
        self.session.get.assert_called_once_with(
            "zones/zone-id/recordsets/recordset-id",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )

        self.assertIsInstance(recordset, _recordset.Recordset)
        self.assertEqual("2c9eb155587228570158722b6ac30007", recordset.id)
        self.assertEqual("www.example.com.", recordset.name)
        self.assertEqual("This is an example record set.",
                         recordset.description)
        self.assertEqual("A", recordset.type)
        self.assertEqual(300, recordset.ttl)
        self.assertEqual(["192.168.10.2", "192.168.10.1"], recordset.records)
        self.assertEqual("PENDING_CREATE", recordset.status)
        self.assertEqual("zone-id", recordset.zone_id)
        self.assertEqual("example.com.", recordset.zone_name)
        self.assertEqual("2016-11-17T12:03:17.827", recordset.create_at)
        self.assertEqual("e55c6f3dc4e34c9f86353b664ae0e70c",
                         recordset.project_id)
        self.assertFalse(recordset.is_default)

    def test_delete_recordset_with_id(self):
        self.proxy.delete_recordset("zone-id", "recordset-id")
        self.assert_session_delete("zones/zone-id/recordsets/recordset-id")

    def test_delete_recordset_with_id2(self):
        self.proxy.delete_recordset(_zone.Zone(id="zone-id"), "recordset-id")
        self.assert_session_delete("zones/zone-id/recordsets/recordset-id")

    def test_delete_recordset_with_instance(self):
        self.proxy.delete_recordset("zone-id",
                                    _recordset.Recordset(id="recordset-id"))
        self.assert_session_delete("zones/zone-id/recordsets/recordset-id")

    def test_delete_recordset_with_instance2(self):
        self.proxy.delete_recordset(_zone.Zone(id="zone-id"),
                                    _recordset.Recordset(id="recordset-id"))
        self.assert_session_delete("zones/zone-id/recordsets/recordset-id")


class TestPTR(TestDNSProxy):
    def __init__(self, *args, **kwargs):
        super(TestPTR, self).__init__(*args, **kwargs)

    def test_create_ptr(self):
        self.mock_response_json_file_values("create_ptr_response.json")

        data = {
            'region': 'eu-de',
            'floating_ip_id': '9e9c6d33-51a6-4f84-b504-c13301f1cc8c',
            'ptrdname': 'www.turnbig.net',
            'description': 'HaveFun.lee - For Test',
            'ttl': 300,
        }

        expect = {
            'region': 'eu-de',
            'floatingip_id': '9e9c6d33-51a6-4f84-b504-c13301f1cc8c',
            'ptrdname': 'www.turnbig.net',
            'description': 'HaveFun.lee - For Test',
            'ttl': 300,
        }
        ptr = self.proxy.create_ptr(**data)
        self.assert_session_patch_with(
            "reverse/floatingips/eu-de:9e9c6d33-51a6-4f84-b504-c13301f1cc8c",
            json=expect)

        self.assertIsInstance(ptr, _ptr.PTR)
        self.assertEqual("region_id:c5504932-bf23-4171-b655-b87a6bc59334",
                         ptr.id)
        self.assertEqual("www.example.com.", ptr.ptrdname)
        self.assertEqual("Description for this PTR record",
                         ptr.description)
        self.assertEqual("10.154.52.138", ptr.address)
        self.assertEqual("CREATE", ptr.action)
        self.assertEqual(300, ptr.ttl)
        self.assertEqual("PENDING_CREATE", ptr.status)

    def test_list_ptr(self):
        query = {
            "marker": "last-ptr-id",
            "limit": 20
        }
        self.mock_response_json_file_values("list_ptr_response.json")
        ptrs = list(self.proxy.ptrs(**query))
        self.assert_session_list_with("/reverse/floatingips", params=query)
        self.assertEqual(1, len(ptrs))
        ptr = ptrs[0]
        self.assertIsInstance(ptr, _ptr.PTR)
        self.assertEqual("region_id:c5504932-bf23-4171-b655-b87a6bc59334",
                         ptr.id)
        self.assertEqual("www.example.com.", ptr.ptrdname)
        self.assertEqual("Description for this PTR record",
                         ptr.description)
        self.assertEqual("10.154.52.138", ptr.address)
        self.assertEqual("NONE", ptr.action)
        self.assertEqual(300, ptr.ttl)
        self.assertEqual("ACTIVE", ptr.status)

    def test_get_ptr_with_id(self):
        self.mock_response_json_file_values("get_ptr_response.json")
        region = 'eu-de'
        floating_ip_id = '9e9c6d33-51a6-4f84-b504-c13301f1cc8c'
        ptr = self.proxy.get_ptr(region, floating_ip_id)
        self.assert_session_get_with(
            "reverse/floatingips/eu-de:9e9c6d33-51a6-4f84-b504-c13301f1cc8c")

        self.assertIsInstance(ptr, _ptr.PTR)
        self.assertEqual("region_id:c5504932-bf23-4171-b655-b87a6bc59334",
                         ptr.id)
        self.assertEqual("www.example.com.", ptr.ptrdname)
        self.assertEqual("Description for this PTR record",
                         ptr.description)
        self.assertEqual("10.154.52.138", ptr.address)
        self.assertEqual("CREATE", ptr.action)
        self.assertEqual(300, ptr.ttl)
        self.assertEqual("ACTIVE", ptr.status)

    def test_restore_ptr_with_id(self):
        region = 'eu-de'
        floating_ip_id = '9e9c6d33-51a6-4f84-b504-c13301f1cc8c'
        ptr = self.proxy.restore_ptr(region, floating_ip_id)
        self.assert_session_patch_with(
            "reverse/floatingips/eu-de:9e9c6d33-51a6-4f84-b504-c13301f1cc8c",
            json={"ptrdname": None}
        )
