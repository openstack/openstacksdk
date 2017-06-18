# -*- coding: utf-8 -*-

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
test_rebuild_server
----------------------------------

Tests for the `rebuild_server` command.
"""

import uuid

from shade import exc
from shade.tests import fakes
from shade.tests.unit import base


class TestRebuildServer(base.RequestsMockTestCase):

    def setUp(self):
        super(TestRebuildServer, self).setUp()
        self.server_id = str(uuid.uuid4())
        self.server_name = self.getUniqueString('name')
        self.fake_server = fakes.make_fake_server(
            self.server_id, self.server_name)
        self.rebuild_server = fakes.make_fake_server(
            self.server_id, self.server_name, 'REBUILD')
        self.error_server = fakes.make_fake_server(
            self.server_id, self.server_name, 'ERROR')

    def test_rebuild_server_rebuild_exception(self):
        """
        Test that an exception in the rebuild raises an exception in
        rebuild_server.
        """
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', self.server_id, 'action']),
                 status_code=400,
                 validate=dict(
                     json={
                         'rebuild': {
                             'imageRef': 'a',
                             'adminPass': 'b'}})),
        ])

        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.rebuild_server,
            self.fake_server['id'], "a", "b")

        self.assert_calls()

    def test_rebuild_server_server_error(self):
        """
        Test that a server error while waiting for the server to rebuild
        raises an exception in rebuild_server.
        """
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', self.server_id, 'action']),
                 json={'server': self.rebuild_server},
                 validate=dict(
                     json={
                         'rebuild': {
                             'imageRef': 'a'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [self.error_server]}),
        ])
        self.assertRaises(
            exc.OpenStackCloudException,
            self.cloud.rebuild_server, self.fake_server['id'], "a", wait=True)

        self.assert_calls()

    def test_rebuild_server_timeout(self):
        """
        Test that a timeout while waiting for the server to rebuild raises an
        exception in rebuild_server.
        """
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', self.server_id, 'action']),
                 json={'server': self.rebuild_server},
                 validate=dict(
                     json={
                         'rebuild': {
                             'imageRef': 'a'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [self.rebuild_server]}),
        ])
        self.assertRaises(
            exc.OpenStackCloudTimeout,
            self.cloud.rebuild_server,
            self.fake_server['id'], "a", wait=True, timeout=0.001)

        self.assert_calls(do_count=False)

    def test_rebuild_server_no_wait(self):
        """
        Test that rebuild_server with no wait and no exception in the
        rebuild call returns the server instance.
        """
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', self.server_id, 'action']),
                 json={'server': self.rebuild_server},
                 validate=dict(
                     json={
                         'rebuild': {
                             'imageRef': 'a'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
        ])
        self.assertEqual(
            self.rebuild_server['status'],
            self.cloud.rebuild_server(self.fake_server['id'], "a")['status'])

        self.assert_calls()

    def test_rebuild_server_with_admin_pass_no_wait(self):
        """
        Test that a server with an admin_pass passed returns the password
        """
        password = self.getUniqueString('password')
        rebuild_server = self.rebuild_server.copy()
        rebuild_server['adminPass'] = password

        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', self.server_id, 'action']),
                 json={'server': rebuild_server},
                 validate=dict(
                     json={
                         'rebuild': {
                             'imageRef': 'a',
                             'adminPass': password}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
        ])
        self.assertEqual(
            password,
            self.cloud.rebuild_server(
                self.fake_server['id'], 'a',
                admin_pass=password)['adminPass'])

        self.assert_calls()

    def test_rebuild_server_with_admin_pass_wait(self):
        """
        Test that a server with an admin_pass passed returns the password
        """
        password = self.getUniqueString('password')
        rebuild_server = self.rebuild_server.copy()
        rebuild_server['adminPass'] = password

        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', self.server_id, 'action']),
                 json={'server': rebuild_server},
                 validate=dict(
                     json={
                         'rebuild': {
                             'imageRef': 'a',
                             'adminPass': password}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [self.rebuild_server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [self.fake_server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
        ])

        self.assertEqual(
            password,
            self.cloud.rebuild_server(
                self.fake_server['id'], 'a',
                admin_pass=password, wait=True)['adminPass'])

        self.assert_calls()

    def test_rebuild_server_wait(self):
        """
        Test that rebuild_server with a wait returns the server instance when
        its status changes to "ACTIVE".
        """
        self.register_uris([
            dict(method='POST',
                 uri=self.get_mock_url(
                     'compute', 'public',
                     append=['servers', self.server_id, 'action']),
                 json={'server': self.rebuild_server},
                 validate=dict(
                     json={
                         'rebuild': {
                             'imageRef': 'a'}})),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [self.rebuild_server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [self.fake_server]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'network', 'public', append=['v2.0', 'networks.json']),
                 json={'networks': []}),
        ])
        self.assertEqual(
            'ACTIVE',
            self.cloud.rebuild_server(
                self.fake_server['id'], 'a', wait=True)['status'])

        self.assert_calls()
