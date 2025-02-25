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


class TestAccessRule(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.user_id = self.operator_cloud.current_user_id

    def _create_application_credential_with_access_rule(self):
        """create application credential with access_rule."""

        app_cred = self.operator_cloud.identity.create_application_credential(
            user=self.user_id,
            name='app_cred',
            access_rules=[
                {
                    "path": "/v2.0/metrics",
                    "service": "monitoring",
                    "method": "GET",
                }
            ],
        )
        self.addCleanup(
            self.operator_cloud.identity.delete_application_credential,
            self.user_id,
            app_cred['id'],
        )
        return app_cred

    def test_get_access_rule(self):
        app_cred = self._create_application_credential_with_access_rule()
        access_rule_id = app_cred['access_rules'][0]['id']
        access_rule = self.operator_cloud.identity.get_access_rule(
            user=self.user_id, access_rule=access_rule_id
        )
        self.assertEqual(access_rule['id'], access_rule_id)
        self.assertEqual(access_rule['user_id'], self.user_id)

    def test_list_access_rules(self):
        app_cred = self._create_application_credential_with_access_rule()
        access_rule_id = app_cred['access_rules'][0]['id']
        access_rules = self.operator_cloud.identity.access_rules(
            user=self.user_id
        )
        self.assertEqual(1, len(list(access_rules)))
        for access_rule in access_rules:
            self.assertEqual(app_cred['user_id'], self.user_id)
            self.assertEqual(access_rule_id, access_rule['id'])

    def test_delete_access_rule(self):
        app_cred = self._create_application_credential_with_access_rule()
        access_rule_id = app_cred['access_rules'][0]['id']

        # This is expected to raise an exception since access_rule is still
        # in use for app_cred.
        self.assertRaises(
            exceptions.HttpException,
            self.operator_cloud.identity.delete_access_rule,
            user=self.user_id,
            access_rule=access_rule_id,
        )

        # delete application credential first to delete access rule
        self.operator_cloud.identity.delete_application_credential(
            user=self.user_id, application_credential=app_cred['id']
        )
        # delete orphaned access rules
        self.operator_cloud.identity.delete_access_rule(
            user=self.user_id, access_rule=access_rule_id
        )
