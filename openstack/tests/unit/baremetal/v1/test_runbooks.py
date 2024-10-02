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

from openstack.baremetal.v1 import runbooks
from openstack.tests.unit import base


FAKE = {
    "created_at": "2024-08-18T22:28:48.643434+11:11",
    "extra": {},
    "links": [
        {
            "href": """http://10.60.253.180:6385/v1/runbooks
                    /bbb45f41-d4bc-4307-8d1d-32f95ce1e920""",
            "rel": "self",
        },
        {
            "href": """http://10.60.253.180:6385/runbooks
                   /bbb45f41-d4bc-4307-8d1d-32f95ce1e920""",
            "rel": "bookmark",
        },
    ],
    "name": "CUSTOM_AWESOME",
    "public": False,
    "owner": "blah",
    "steps": [
        {
            "args": {
                "settings": [{"name": "LogicalProc", "value": "Enabled"}]
            },
            "interface": "bios",
            "order": 1,
            "step": "apply_configuration",
        }
    ],
    "updated_at": None,
    "uuid": "32f95ce1-4307-d4bc-8d1d-e920bbb45f41",
}


class Runbooks(base.TestCase):
    def test_basic(self):
        sot = runbooks.Runbook()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('runbooks', sot.resources_key)
        self.assertEqual('/runbooks', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

    def test_instantiate(self):
        sot = runbooks.Runbook(**FAKE)
        self.assertEqual(FAKE['steps'], sot.steps)
        self.assertEqual(FAKE['created_at'], sot.created_at)
        self.assertEqual(FAKE['extra'], sot.extra)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['public'], sot.public)
        self.assertEqual(FAKE['owner'], sot.owner)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)
        self.assertEqual(FAKE['uuid'], sot.id)
