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

from openstack.baremetal.v1 import volume_connector
from openstack.tests.unit import base


FAKE = {
    "connector_id": "iqn.2017-07.org.openstack:01:d9a51732c3f",
    "created_at": "2016-08-18T22:28:48.643434+11:11",
    "extra": {},
    "links": [
        {
            "href": "http://127.0.0.1:6385/v1/volume/connector/<ID>",
            "rel": "self",
        },
        {
            "href": "http://127.0.0.1:6385/volume/connector/<ID>",
            "rel": "bookmark",
        },
    ],
    "node_uuid": "6d85703a-565d-469a-96ce-30b6de53079d",
    "type": "iqn",
    "updated_at": None,
    "uuid": "9bf93e01-d728-47a3-ad4b-5e66a835037c",
}


class TestVolumeconnector(base.TestCase):
    def test_basic(self):
        sot = volume_connector.VolumeConnector()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('connectors', sot.resources_key)
        self.assertEqual('/volume/connectors', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

    def test_instantiate(self):
        sot = volume_connector.VolumeConnector(**FAKE)
        self.assertEqual(FAKE['connector_id'], sot.connector_id)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['extra'], sot.extra)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['node_uuid'], sot.node_id)
        self.assertEqual(FAKE['type'], sot.type)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)
        self.assertEqual(FAKE['uuid'], sot.id)
