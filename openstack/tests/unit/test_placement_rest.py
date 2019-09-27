# Copyright (c) 2018 Red Hat, Inc.

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

import ddt
from keystoneauth1 import exceptions

from openstack.tests.unit import base


@ddt.ddt
class TestPlacementRest(base.TestCase):

    def setUp(self):
        super(TestPlacementRest, self).setUp()
        self.use_placement()

    def _register_uris(self, status_code=None):
        uri = dict(
            method='GET',
            uri=self.get_mock_url(
                'placement', 'public', append=['allocation_candidates']),
            json={})
        if status_code is not None:
            uri['status_code'] = status_code
        self.register_uris([uri])

    def _validate_resp(self, resp, status_code):
        self.assertEqual(status_code, resp.status_code)
        self.assertEqual(
            'https://placement.example.com/allocation_candidates',
            resp.url)
        self.assert_calls()

    @ddt.data({}, {'raise_exc': False}, {'raise_exc': True})
    def test_discovery(self, get_kwargs):
        self._register_uris()
        # Regardless of raise_exc, a <400 response doesn't raise
        rs = self.cloud.placement.get('/allocation_candidates', **get_kwargs)
        self._validate_resp(rs, 200)

    @ddt.data({}, {'raise_exc': False})
    def test_discovery_err(self, get_kwargs):
        self._register_uris(status_code=500)
        # >=400 doesn't raise by default or with explicit raise_exc=False
        rs = self.cloud.placement.get('/allocation_candidates', **get_kwargs)
        self._validate_resp(rs, 500)

    def test_discovery_exc(self):
        self._register_uris(status_code=500)
        # raise_exc=True raises a ksa exception appropriate to the status code
        ex = self.assertRaises(
            exceptions.InternalServerError,
            self.cloud.placement.get, '/allocation_candidates', raise_exc=True)
        self._validate_resp(ex.response, 500)

    def test_microversion_discovery(self):
        self.assertEqual(
            (1, 17),
            self.cloud.placement.get_endpoint_data().max_microversion)
        self.assert_calls()
