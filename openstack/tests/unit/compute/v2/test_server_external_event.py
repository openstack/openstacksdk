# Copyright 2026 Openinfra Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from openstack.compute.v2 import server_external_event
from openstack.tests.unit import base


EXAMPLE = {
    'name': 'testevent',
    'server_uuid': 'SERVER_UUID',
    'status': 'completed',
    'tag': 'MYTAG',
}


class TestServerExternalEvent(base.TestCase):
    def test_basic(self):
        sot = server_external_event.ServerExternalEvent()
        self.assertEqual('event', sot.resource_key)
        self.assertEqual('events', sot.resources_key)
        self.assertEqual('/os-server-external-events', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = server_external_event.ServerExternalEvent(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['server_uuid'], sot.server_uuid)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['tag'], sot.tag)
