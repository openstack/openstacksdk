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

from typing import Any
from unittest import mock

from keystoneauth1 import adapter

from openstack.baremetal.v1 import _common
from openstack.baremetal.v1 import runbooks
from openstack import exceptions
from openstack.tests.unit import base
from openstack import utils


FAKE: dict[str, Any] = {
    "created_at": "2024-08-18T22:28:48.643434+11:11",
    "description": "Enable logical processors",
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
    "traits": ["CUSTOM_AWESOME"],
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
        self.assertEqual(FAKE['description'], sot.description)
        self.assertEqual(FAKE['extra'], sot.extra)
        self.assertEqual(FAKE['links'], sot.links)
        self.assertEqual(FAKE['name'], sot.name)
        self.assertEqual(FAKE['public'], sot.public)
        self.assertEqual(FAKE['owner'], sot.owner)
        self.assertEqual(FAKE['traits'], sot.traits)
        self.assertEqual(FAKE['updated_at'], sot.updated_at)
        self.assertEqual(FAKE['uuid'], sot.id)


@mock.patch.object(utils, 'pick_microversion', lambda session, v: v)
@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestRunbookTraits(base.TestCase):
    def setUp(self):
        super().setUp()
        self.runbook = runbooks.Runbook(**FAKE)
        self.session = mock.Mock(
            spec=adapter.Adapter, default_microversion='1.112'
        )
        self.session.log = mock.Mock()

    def test_add_trait(self):
        self.runbook.add_trait(self.session, 'CUSTOM_FAKE')
        self.session.put.assert_called_once_with(
            'runbooks/{}/traits/{}'.format(self.runbook.id, 'CUSTOM_FAKE'),
            json=None,
            headers=mock.ANY,
            microversion='1.112',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )
        self.assertEqual(
            {'CUSTOM_AWESOME', 'CUSTOM_FAKE'}, set(self.runbook.traits)
        )

    def test_remove_trait(self):
        self.runbook.remove_trait(self.session, 'CUSTOM_AWESOME')
        self.session.delete.assert_called_once_with(
            'runbooks/{}/traits/{}'.format(self.runbook.id, 'CUSTOM_AWESOME'),
            headers=mock.ANY,
            microversion='1.112',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )
        self.assertEqual([], self.runbook.traits)

    def test_set_traits(self):
        traits = ['CUSTOM_FAKE', 'CUSTOM_REAL']
        self.runbook.set_traits(self.session, traits)
        self.session.put.assert_called_once_with(
            f'runbooks/{self.runbook.id}/traits',
            json={'traits': traits},
            headers=mock.ANY,
            microversion='1.112',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )
        self.assertEqual(traits, self.runbook.traits)

    def test_set_traits_empty(self):
        self.runbook.set_traits(self.session, [])
        self.session.put.assert_called_once_with(
            f'runbooks/{self.runbook.id}/traits',
            json={'traits': []},
            headers=mock.ANY,
            microversion='1.112',
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )
        self.assertEqual([], self.runbook.traits)
