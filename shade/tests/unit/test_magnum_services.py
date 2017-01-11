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


import mock
import munch

import shade
from shade.tests.unit import base


magnum_service_obj = munch.Munch(
    binary='fake-service',
    state='up',
    report_count=1,
    human_id=None,
    host='fake-host',
    id=1,
    disabled_reason=None
)


class TestMagnumServices(base.TestCase):

    @mock.patch.object(shade.OpenStackCloud, 'magnum_client')
    def test_list_magnum_services(self, mock_magnum):
        mock_magnum.mservices.list.return_value = [magnum_service_obj, ]
        mservices_list = self.op_cloud.list_magnum_services()
        mock_magnum.mservices.list.assert_called_with(detail=False)
        self.assertEqual(mservices_list[0], magnum_service_obj)
