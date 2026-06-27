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

from openstack.shared_file_system.v2 import service
from openstack.tests.unit import base


EXAMPLE = {
    "status": "enabled",
    "binary": "manila-share",
    "zone": "nova",
    "host": "manila2@generic1",
    "updated_at": "2021-06-07T13:03:57.000000",
    "state": "up",
    "id": 1,
}


class TestServices(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = {'service': {}}
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.status_code = 200
        self.resp.headers = {}
        self.sess = mock.Mock()
        self.sess.put = mock.Mock(return_value=self.resp)

    def test_basic(self):
        services_resource = service.Service()
        self.assertEqual('services', services_resource.resources_key)
        self.assertEqual('/services', services_resource.base_path)
        self.assertTrue(services_resource.allow_list)
        self.assertFalse(services_resource.allow_create)
        self.assertFalse(services_resource.allow_fetch)
        self.assertTrue(services_resource.allow_commit)
        self.assertFalse(services_resource.allow_delete)
        self.assertFalse(services_resource.allow_head)

        self.assertDictEqual(
            {
                'binary': 'binary',
                'host': 'host',
                'limit': 'limit',
                'state': 'state',
                'status': 'status',
                'marker': 'marker',
                'name': 'binary',
                'availability_zone': 'zone',
            },
            services_resource._query_mapping._mapping,
        )

    def test_make_services(self):
        services_resource = service.Service(**EXAMPLE)
        self.assertEqual(EXAMPLE['id'], services_resource.id)
        self.assertEqual(EXAMPLE['status'], services_resource.status)
        self.assertEqual(EXAMPLE['binary'], services_resource.binary)
        self.assertEqual(EXAMPLE['zone'], services_resource.availability_zone)
        self.assertEqual(EXAMPLE['host'], services_resource.host)
        self.assertEqual(EXAMPLE['updated_at'], services_resource.updated_at)
        self.assertEqual(EXAMPLE['state'], services_resource.state)

    def test_enable(self):
        sot = service.Service(**EXAMPLE)

        res = sot.enable(self.sess)
        self.assertIsNotNone(res)

        url = 'services/enable'
        body = {
            'binary': EXAMPLE['binary'],
            'host': EXAMPLE['host'],
        }
        self.sess.put.assert_called_with(
            url, json=body, microversion=self.sess.default_microversion
        )

    def test_disable(self):
        sot = service.Service(**EXAMPLE)

        res = sot.disable(self.sess)
        self.assertIsNotNone(res)

        url = 'services/disable'
        body = {
            'binary': EXAMPLE['binary'],
            'host': EXAMPLE['host'],
        }
        self.sess.put.assert_called_with(
            url, json=body, microversion=self.sess.default_microversion
        )

    def test_disable_with_reason(self):
        sot = service.Service(**EXAMPLE)

        res = sot.disable(self.sess, disable_reason='maintenance')
        self.assertIsNotNone(res)

        url = 'services/disable'
        body = {
            'binary': EXAMPLE['binary'],
            'host': EXAMPLE['host'],
            'disabled_reason': 'maintenance',
        }
        self.sess.put.assert_called_with(
            url, json=body, microversion=self.sess.default_microversion
        )

    def test_ensure_shares(self):
        self.resp.status_code = 202
        self.sess.post = mock.Mock(return_value=self.resp)

        sot = service.Service(**EXAMPLE)
        sot.ensure_shares(self.sess)

        url = 'services/ensure-shares'
        body = {'host': EXAMPLE['host']}
        self.sess.post.assert_called_with(
            url, json=body, microversion=self.sess.default_microversion
        )
