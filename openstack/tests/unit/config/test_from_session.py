# Copyright 2018 Red Hat, Inc.
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

from testscenarios import load_tests_apply_scenarios as load_tests  # noqa

import uuid

from openstack.config import cloud_region
from openstack import connection
from openstack.tests import fakes
from openstack.tests.unit import base


class TestFromSession(base.TestCase):

    scenarios = [
        ('no_region', dict(test_region=None)),
        ('with_region', dict(test_region='RegionOne')),
    ]

    def test_from_session(self):
        config = cloud_region.from_session(
            self.cloud.session, region_name=self.test_region)
        self.assertEqual(config.name, 'identity.example.com')
        if not self.test_region:
            self.assertIsNone(config.region_name)
        else:
            self.assertEqual(config.region_name, self.test_region)

        server_id = str(uuid.uuid4())
        server_name = self.getUniqueString('name')
        fake_server = fakes.make_fake_server(server_id, server_name)
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [fake_server]}),
        ])

        conn = connection.Connection(config=config)
        s = next(conn.compute.servers())
        self.assertEqual(s.id, server_id)
        self.assertEqual(s.name, server_name)
        self.assert_calls()
