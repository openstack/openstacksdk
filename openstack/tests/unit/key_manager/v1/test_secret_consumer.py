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

from unittest import mock

from keystoneauth1 import adapter

from openstack.key_manager.v1 import secret_consumer
from openstack.tests.unit import base


EXAMPLE = {
    'secret_id': 'sid',
    'service': 'svc',
    'resource_type': 'type',
    'resource_id': 'rid',
}


class TestSecretConsumer(base.TestCase):
    def test_basic(self):
        sot = secret_consumer.SecretConsumer()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('consumers', sot.resources_key)
        self.assertEqual('/secrets/%(secret_id)s/consumers', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.requires_id)

    def test_make_it(self):
        sot = secret_consumer.SecretConsumer(**EXAMPLE)
        self.assertEqual(EXAMPLE['secret_id'], sot.secret_id)
        self.assertEqual(EXAMPLE['service'], sot.service)
        self.assertEqual(EXAMPLE['resource_type'], sot.resource_type)
        self.assertEqual(EXAMPLE['resource_id'], sot.resource_id)

    def test_delete_with_body(self):
        sot = secret_consumer.SecretConsumer(
            secret_id="sid",
            service="svc",
            resource_type="type",
            resource_id="rid",
        )
        session = mock.Mock(spec=adapter.Adapter)
        session.default_microversion = None
        delete_resp = mock.Mock()
        delete_resp.status_code = 204
        delete_resp.headers = {}
        session.delete.return_value = delete_resp

        sot._raw_delete(session)

        session.delete.assert_called_once()
        _, kwargs = session.delete.call_args
        self.assertEqual(
            {"service": "svc", "resource_type": "type", "resource_id": "rid"},
            kwargs["json"],
        )
