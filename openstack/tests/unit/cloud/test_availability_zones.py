# Copyright (c) 2017 Red Hat, Inc.
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

from openstack.tests import fakes
from openstack.tests.unit import base


_fake_zone_list = {
    "availabilityZoneInfo": [
        {"hosts": None, "zoneName": "az1", "zoneState": {"available": True}},
        {"hosts": None, "zoneName": "nova", "zoneState": {"available": False}},
    ]
}


class TestAvailabilityZoneNames(base.TestCase):
    def test_list_availability_zone_names(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-availability-zone',
                    json=_fake_zone_list,
                ),
            ]
        )

        self.assertEqual(['az1'], self.cloud.list_availability_zone_names())

        self.assert_calls()

    def test_unauthorized_availability_zone_names(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-availability-zone',
                    status_code=403,
                ),
            ]
        )

        self.assertEqual([], self.cloud.list_availability_zone_names())

        self.assert_calls()

    def test_list_all_availability_zone_names(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/os-availability-zone',
                    json=_fake_zone_list,
                ),
            ]
        )

        self.assertEqual(
            ['az1', 'nova'],
            self.cloud.list_availability_zone_names(unavailable=True),
        )

        self.assert_calls()
