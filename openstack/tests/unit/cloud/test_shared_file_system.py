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

import uuid

from openstack.tests.unit import base


IDENTIFIER = str(uuid.uuid4())
MANILA_AZ_DICT = {
    "id": IDENTIFIER,
    "name": "manila-zone-0",
    "created_at": "2021-01-21T20:13:55.000000",
    "updated_at": None,
}


class TestSharedFileSystem(base.TestCase):
    def setUp(self):
        super().setUp()
        self.use_manila()

    def test_list_availability_zones(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        'shared-file-system',
                        'public',
                        append=['v2', 'availability-zones'],
                    ),
                    json={'availability_zones': [MANILA_AZ_DICT]},
                ),
            ]
        )
        az_list = self.cloud.list_share_availability_zones()
        self.assertEqual(len(az_list), 1)
        self.assertEqual(MANILA_AZ_DICT['id'], az_list[0].id)
        self.assertEqual(MANILA_AZ_DICT['name'], az_list[0].name)
        self.assertEqual(MANILA_AZ_DICT['created_at'], az_list[0].created_at)
        self.assertEqual(MANILA_AZ_DICT['updated_at'], az_list[0].updated_at)
        self.assert_calls()
