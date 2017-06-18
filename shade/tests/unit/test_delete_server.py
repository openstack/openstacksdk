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

"""
test_delete_server
----------------------------------

Tests for the `delete_server` command.
"""

from shade import exc as shade_exc
from shade.tests import fakes
from shade.tests.unit import base


class TestDeleteServer(base.RequestsMockTestCase):

    def test_delete_server(self):
        """
        Test that server delete is called when wait=False
        """
        server = fakes.make_fake_server('1234', 'daffy', 'ACTIVE')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234'])),
        ])
        self.assertTrue(self.cloud.delete_server('daffy', wait=False))

        self.assert_calls()

    def test_delete_server_already_gone(self):
        """
        Test that we return immediately when server is already gone
        """
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': []}),
        ])
        self.assertFalse(self.cloud.delete_server('tweety', wait=False))

        self.assert_calls()

    def test_delete_server_already_gone_wait(self):
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': []}),
        ])
        self.assertFalse(self.cloud.delete_server('speedy', wait=True))
        self.assert_calls()

    def test_delete_server_wait_for_deleted(self):
        """
        Test that delete_server waits for the server to be gone
        """
        server = fakes.make_fake_server('9999', 'wily', 'ACTIVE')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '9999'])),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': []}),
        ])
        self.assertTrue(self.cloud.delete_server('wily', wait=True))

        self.assert_calls()

    def test_delete_server_fails(self):
        """
        Test that delete_server raises non-404 exceptions
        """
        server = fakes.make_fake_server('1212', 'speedy', 'ACTIVE')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1212']),
                 status_code=400),
        ])

        self.assertRaises(
            shade_exc.OpenStackCloudException,
            self.cloud.delete_server, 'speedy',
            wait=False)

        self.assert_calls()

    def test_delete_server_no_cinder(self):
        """
        Test that deleting server works when cinder is not available
        """
        orig_has_service = self.cloud.has_service

        def fake_has_service(service_type):
            if service_type == 'volume':
                return False
            return orig_has_service(service_type)
        self.cloud.has_service = fake_has_service

        server = fakes.make_fake_server('1234', 'porky', 'ACTIVE')
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [server]}),
            dict(method='DELETE',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', '1234'])),
        ])
        self.assertTrue(self.cloud.delete_server('porky', wait=False))

        self.assert_calls()
