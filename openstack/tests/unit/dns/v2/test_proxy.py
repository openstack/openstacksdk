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

from openstack.dns.v2 import _proxy
from openstack.dns.v2 import zone
from openstack.dns.v2 import zone_import
from openstack.dns.v2 import zone_export
from openstack.dns.v2 import zone_transfer
from openstack.dns.v2 import recordset
from openstack.dns.v2 import floating_ip
from openstack.tests.unit import test_proxy_base


class TestDnsProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestDnsProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestDnsZone(TestDnsProxy):
    def test_zone_create(self):
        self.verify_create(self.proxy.create_zone, zone.Zone,
                           method_kwargs={'name': 'id'},
                           expected_kwargs={'name': 'id',
                                            'prepend_key': False})

    def test_zone_delete(self):
        self.verify_delete(self.proxy.delete_zone,
                           zone.Zone, True)

    def test_zone_find(self):
        self.verify_find(self.proxy.find_zone, zone.Zone)

    def test_zone_get(self):
        self.verify_get(self.proxy.get_zone, zone.Zone)

    def test_zones(self):
        self.verify_list(self.proxy.zones, zone.Zone)

    def test_zone_update(self):
        self.verify_update(self.proxy.update_zone, zone.Zone)

    def test_zone_abandon(self):
        self._verify2("openstack.dns.v2.zone.Zone.abandon",
                      self.proxy.abandon_zone,
                      method_args=[{'zone': 'id'}],
                      expected_args=[self.proxy])

    def test_zone_xfr(self):
        self._verify2("openstack.dns.v2.zone.Zone.xfr",
                      self.proxy.xfr_zone,
                      method_args=[{'zone': 'id'}],
                      expected_args=[self.proxy])


class TestDnsRecordset(TestDnsProxy):
    def test_recordset_create(self):
        self.verify_create(self.proxy.create_recordset, recordset.Recordset,
                           method_kwargs={'zone': 'id'},
                           expected_kwargs={'zone_id': 'id',
                                            'prepend_key': False})

    def test_recordset_delete(self):
        self.verify_delete(self.proxy.delete_recordset,
                           recordset.Recordset, True)

    def test_recordset_update(self):
        self.verify_update(self.proxy.update_recordset, recordset.Recordset)

    def test_recordset_get(self):
        self.verify_get(self.proxy.get_recordset, recordset.Recordset,
                        method_kwargs={'zone': 'zid'},
                        expected_kwargs={'zone_id': 'zid'}
                        )

    def test_recordsets(self):
        self.verify_list(self.proxy.recordsets, recordset.Recordset,
                         base_path='/recordsets')

    def test_recordsets_zone(self):
        self.verify_list(self.proxy.recordsets, recordset.Recordset,
                         method_kwargs={'zone': 'zid'},
                         expected_kwargs={'zone_id': 'zid'})

    def test_recordset_find(self):
        self._verify2("openstack.proxy.Proxy._find",
                      self.proxy.find_recordset,
                      method_args=['zone', 'rs'],
                      method_kwargs={},
                      expected_args=[recordset.Recordset, 'rs'],
                      expected_kwargs={'ignore_missing': True,
                                       'zone_id': 'zone'})


class TestDnsFloatIP(TestDnsProxy):
    def test_floating_ips(self):
        self.verify_list(self.proxy.floating_ips, floating_ip.FloatingIP)

    def test_floating_ip_get(self):
        self.verify_get(self.proxy.get_floating_ip, floating_ip.FloatingIP)

    def test_floating_ip_update(self):
        self.verify_update(self.proxy.update_floating_ip,
                           floating_ip.FloatingIP)


class TestDnsZoneImport(TestDnsProxy):
    def test_zone_import_delete(self):
        self.verify_delete(self.proxy.delete_zone_import,
                           zone_import.ZoneImport, True)

    def test_zone_import_get(self):
        self.verify_get(self.proxy.get_zone_import, zone_import.ZoneImport)

    def test_zone_imports(self):
        self.verify_list(self.proxy.zone_imports, zone_import.ZoneImport)

    def test_zone_import_create(self):
        self.verify_create(self.proxy.create_zone_import,
                           zone_import.ZoneImport,
                           method_kwargs={'name': 'id'},
                           expected_kwargs={'name': 'id',
                                            'prepend_key': False})


class TestDnsZoneExport(TestDnsProxy):
    def test_zone_export_delete(self):
        self.verify_delete(self.proxy.delete_zone_export,
                           zone_export.ZoneExport, True)

    def test_zone_export_get(self):
        self.verify_get(self.proxy.get_zone_export, zone_export.ZoneExport)

    def test_zone_export_get_text(self):
        self.verify_get(self.proxy.get_zone_export_text,
                        zone_export.ZoneExport,
                        value=[{'id': 'zone_export_id_value'}],
                        expected_kwargs={
                            'base_path': '/zones/tasks/export/%(id)s/export'
                        })

    def test_zone_exports(self):
        self.verify_list(self.proxy.zone_exports, zone_export.ZoneExport)

    def test_zone_export_create(self):
        self.verify_create(self.proxy.create_zone_export,
                           zone_export.ZoneExport,
                           method_args=[{'id': 'zone_id_value'}],
                           method_kwargs={'name': 'id'},
                           expected_kwargs={'name': 'id',
                                            'zone_id': 'zone_id_value',
                                            'prepend_key': False})


class TestDnsZoneTransferRequest(TestDnsProxy):
    def test_zone_transfer_request_delete(self):
        self.verify_delete(self.proxy.delete_zone_transfer_request,
                           zone_transfer.ZoneTransferRequest, True)

    def test_zone_transfer_request_get(self):
        self.verify_get(self.proxy.get_zone_transfer_request,
                        zone_transfer.ZoneTransferRequest)

    def test_zone_transfer_requests(self):
        self.verify_list(self.proxy.zone_transfer_requests,
                         zone_transfer.ZoneTransferRequest)

    def test_zone_transfer_request_create(self):
        self.verify_create(self.proxy.create_zone_transfer_request,
                           zone_transfer.ZoneTransferRequest,
                           method_args=[{'id': 'zone_id_value'}],
                           method_kwargs={'name': 'id'},
                           expected_kwargs={'name': 'id',
                                            'zone_id': 'zone_id_value',
                                            'prepend_key': False})

    def test_zone_transfer_request_update(self):
        self.verify_update(self.proxy.update_zone_transfer_request,
                           zone_transfer.ZoneTransferRequest)


class TestDnsZoneTransferAccept(TestDnsProxy):
    def test_zone_transfer_accept_get(self):
        self.verify_get(self.proxy.get_zone_transfer_accept,
                        zone_transfer.ZoneTransferAccept)

    def test_zone_transfer_accepts(self):
        self.verify_list(self.proxy.zone_transfer_accepts,
                         zone_transfer.ZoneTransferAccept)

    def test_zone_transfer_accept_create(self):
        self.verify_create(self.proxy.create_zone_transfer_accept,
                           zone_transfer.ZoneTransferAccept)
