# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock

import ironicclient
import shade
from shade.tests import base


class TestShadeOperatorNoAuth(base.TestCase):
    def setUp(self):
        """Setup Noauth OperatorCloud tests

        Setup the test to utilize no authentication and an endpoint
        URL in the auth data.  This is permits testing of the basic
        mechanism that enables Ironic noauth mode to be utilized with
        Shade.
        """
        super(TestShadeOperatorNoAuth, self).setUp()
        self.cloud_noauth = shade.operator_cloud(
            auth_type='None',
            auth=dict(endpoint="http://localhost:6385")
        )

    @mock.patch.object(shade.OperatorCloud, 'get_session_endpoint')
    @mock.patch.object(ironicclient.client, 'Client')
    def test_ironic_noauth_selection_using_a_task(
            self, mock_client, mock_endpoint):
        """Test noauth selection for Ironic in OperatorCloud

        Utilize a task to trigger the client connection attempt
        and evaluate if get_session_endpoint was called while the client
        was still called.
        """
        self.cloud_noauth.patch_machine('name', {})
        self.assertFalse(mock_endpoint.called)
        self.assertTrue(mock_client.called)
