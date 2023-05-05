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

from openstack.container_infrastructure_management.v1 import service
from openstack.tests.unit import base


magnum_service_obj = dict(
    binary='fake-service',
    created_at='2015-08-27T09:49:58-05:00',
    disabled_reason=None,
    host='fake-host',
    id=1,
    report_count=1,
    state='up',
    updated_at=None,
)


class TestMagnumServices(base.TestCase):
    def test_list_magnum_services(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=self.get_mock_url(
                        service_type='container-infrastructure-management',
                        resource='mservices',
                    ),
                    json=dict(mservices=[magnum_service_obj]),
                )
            ]
        )
        mservices_list = self.cloud.list_magnum_services()
        self.assertEqual(
            mservices_list[0].to_dict(computed=False),
            service.Service(**magnum_service_obj).to_dict(computed=False),
        )
        self.assert_calls()
