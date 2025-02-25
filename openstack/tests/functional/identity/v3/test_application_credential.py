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

from openstack import exceptions
from openstack.tests.functional import base


class TestApplicationCredentials(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.user_id = self.operator_cloud.current_user_id

    def _create_application_credentials(self):
        app_creds = self.operator_cloud.identity.create_application_credential(
            user=self.user_id, name='app_cred'
        )
        self.addCleanup(
            self.operator_cloud.identity.delete_application_credential,
            self.user_id,
            app_creds['id'],
        )
        return app_creds

    def test_create_application_credentials(self):
        app_creds = self._create_application_credentials()
        self.assertEqual(app_creds['user_id'], self.user_id)

    def test_get_application_credential(self):
        app_creds = self._create_application_credentials()
        app_cred = self.operator_cloud.identity.get_application_credential(
            user=self.user_id, application_credential=app_creds['id']
        )
        self.assertEqual(app_cred['id'], app_creds['id'])
        self.assertEqual(app_cred['user_id'], self.user_id)

    def test_application_credentials(self):
        self._create_application_credentials()
        app_creds = self.operator_cloud.identity.application_credentials(
            user=self.user_id
        )
        for app_cred in app_creds:
            self.assertEqual(app_cred['user_id'], self.user_id)

    def test_find_application_credential(self):
        app_creds = self._create_application_credentials()
        app_cred = self.operator_cloud.identity.find_application_credential(
            user=self.user_id, name_or_id=app_creds['id']
        )
        self.assertEqual(app_cred['id'], app_creds['id'])
        self.assertEqual(app_cred['user_id'], self.user_id)

    def test_delete_application_credential(self):
        app_creds = self._create_application_credentials()
        self.operator_cloud.identity.delete_application_credential(
            user=self.user_id, application_credential=app_creds['id']
        )
        self.assertRaises(
            exceptions.NotFoundException,
            self.operator_cloud.identity.get_application_credential,
            user=self.user_id,
            application_credential=app_creds['id'],
        )
