# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from testtools import matchers

from openstack.tests.unit import base


class TestIdentityUsers(base.TestCase):
    def get_mock_url(
        self,
        service_type='identity',
        interface='public',
        resource='users',
        append=None,
        base_url_append='v3',
        qs_elements=None,
    ):
        return super().get_mock_url(
            service_type,
            interface,
            resource,
            append,
            base_url_append,
            qs_elements,
        )

    def test_create_user(self):
        domain_data = self._get_domain_data()
        user_data = self._get_user_data(
            "myusername", "mypassword", domain_id=domain_data.domain_id
        )
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json=user_data.json_response,
                    validate=dict(json=user_data.json_request),
                )
            ]
        )

        user = self.cloud.create_user(
            user_data.name,
            password=user_data.password,
            domain_id=domain_data.domain_id,
        )

        self.assertIsNotNone(user)
        self.assertThat(user.name, matchers.Equals(user_data.name))
        self.assert_calls()

    def test_create_user_without_password(self):
        domain_data = self._get_domain_data()
        user_data = self._get_user_data(
            "myusername", domain_id=domain_data.domain_id
        )
        user_data._replace(
            password=None,
            json_request=user_data.json_request["user"].pop("password"),
        )

        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=self.get_mock_url(),
                    status_code=200,
                    json=user_data.json_response,
                    validate=dict(json=user_data.json_request),
                )
            ]
        )

        user = self.cloud.create_user(
            user_data.name, domain_id=domain_data.domain_id
        )

        self.assertIsNotNone(user)
        self.assertThat(user.name, matchers.Equals(user_data.name))
        self.assert_calls()
