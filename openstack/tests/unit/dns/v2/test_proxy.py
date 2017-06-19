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
import json

import mock

from openstack import profile
from openstack import session
from openstack.dns import dns_service
from openstack.dns.v2 import _proxy
from openstack.tests.unit import base
from openstack.dns.v2 import name_server as _name_server
from openstack.dns.v2 import recordset as _recordset
from openstack.dns.v2 import router as _router
from openstack.dns.v2 import zone as _zone
from openstack.dns.v2 import ptr as _ptr
from openstack.tests.unit.test_proxy_base3 import BaseProxyTestCase


class TestDNSProxy(BaseProxyTestCase):
    def __init__(self, *args, **kwargs):
        super(TestDNSProxy, self).__init__(
            *args,
            proxy_class=_proxy.Proxy,
            service_class=dns_service.DNSService,
            **kwargs)

    def test_list_zones(self):
        query = {
            'zone_type': 'public',
            'limit': 10
        }
        self.mock_response_json_file_values('list_zone.json')
        zones = list(self.proxy.zones(**query))
        self.assert_session_get_with('/zones', query)
        self.assertEqual(2, len(zones))
        zone = zones[0]
        self.assertEquals(zone.id, '2c9eb155587194ec01587224c9f90149')
        self.assertEquals(zone.name, 'example.com.')

    def test_create_public_zone(self):
        attrs = {
            "name": "example.com.",
            "description": "This is an example zone.",
            "zone_type": "public",
            "email": "xx@example.com"
        }
        self.mock_response_json_file_values('create_public_zone.json')
        zone = self.proxy.create_zone(**attrs)
        self.assert_session_post_with('/zones', json=attrs, header={})
        self.assertEquals(zone.name, 'example.com.')
        self.assertEquals(zone.zone_type, 'public')
        self.assertEquals(zone.email, 'xx@example.com')
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
        self.assert_session_post_with('/zones', json=attrs, header={})
        self.assertEquals(zone.name, 'example.com.')
        self.assertEquals(zone.zone_type, 'private')
        self.assertEquals(zone.email, 'xx@example.com')
        self.assertIsNotNone(zone.router)
        self.assertEquals(zone.router.router_id,
                          "19664294-0bf6-4271-ad3a-94b8c79c6558")
        self.assertEquals(zone.router.router_region, "eu-de")
        self.assertIsNotNone(zone.id)
