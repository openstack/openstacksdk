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

from openstack.tests.unit import base


class TestPlacementRest(base.TestCase):

    def setUp(self):
        super(TestPlacementRest, self).setUp()
        self.use_placement()

    def test_discovery(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'placement', 'public', append=['allocation_candidates']),
                 json={})
        ])
        rs = self.cloud.placement.get('/allocation_candidates')
        self.assertEqual(200, rs.status_code)
        self.assertEqual(
            'https://placement.example.com/allocation_candidates',
            rs.url)
        self.assert_calls()

    def test_microversion_discovery(self):
        self.assertEqual(
            (1, 17),
            self.cloud.placement.get_endpoint_data().max_microversion)
        self.assert_calls()
