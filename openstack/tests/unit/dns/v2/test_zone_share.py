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

from unittest import mock

from keystoneauth1 import adapter

from openstack.dns.v2 import zone_share
from openstack.tests.unit import base


class TestZoneShare(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = None
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.status_code = 200
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.post = mock.Mock(return_value=self.resp)
        self.sess.default_microversion = None

    def test_basic(self):
        sot = zone_share.ZoneShare()
        self.assertEqual(None, sot.resource_key)
        self.assertEqual('shared_zones', sot.resources_key)
        self.assertEqual('/zones/%(zone_id)s/shares', sot.base_path)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertFalse(sot.allow_commit)

        self.assertDictEqual(
            {
                'target_project_id': 'target_project_id',
                'limit': 'limit',
                'marker': 'marker',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        share_id = 'bogus_id'
        zone_id = 'bogus_zone_id'
        project_id = 'bogus_project_id'
        target_id = 'bogus_target_id'
        expected = {
            'id': share_id,
            'zone_id': zone_id,
            'project_id': project_id,
            'target_project_id': target_id,
        }

        sot = zone_share.ZoneShare(**expected)
        self.assertEqual(share_id, sot.id)
        self.assertEqual(zone_id, sot.zone_id)
        self.assertEqual(project_id, sot.project_id)
        self.assertEqual(target_id, sot.target_project_id)
