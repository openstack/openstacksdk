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

from openstack.key_manager.v1 import secret_consumer as _secret_consumer
from openstack.tests.functional import base


class TestSecretConsumer(base.BaseFunctionalTest):
    def setUp(self):
        super().setUp()
        self.require_service('key-manager')

        self.secret = self.operator_cloud.key_manager.create_secret(
            name=self.getUniqueString('secret'),
            payload='functional-secret-consumer-payload',
            payload_content_type='text/plain',
            secret_type='opaque',
        )
        self.secret_id = self.secret.secret_id
        self.assertIsNotNone(self.secret_id)

        self.addCleanup(
            self.operator_cloud.key_manager.delete_secret,
            self.secret_id,
            ignore_missing=True,
        )

    def test_secret_consumer(self):
        key_manager = self.operator_cloud.key_manager

        consumer = key_manager.create_secret_consumer(
            self.secret_id,
            service='image',
            resource_type='image',
            resource_id='123e4567-e89b-12d3-a456-426614174000',
        )
        self.assertIsInstance(consumer, _secret_consumer.SecretConsumer)

        consumers = list(key_manager.secret_consumers(self.secret_id))
        self.assertEqual(1, len(consumers))
        self.assertEqual('image', consumers[0].service)
        self.assertEqual('image', consumers[0].resource_type)

        key_manager.delete_secret_consumer(
            self.secret_id,
            service='image',
            resource_type='image',
            resource_id='123e4567-e89b-12d3-a456-426614174000',
        )

        consumers = list(key_manager.secret_consumers(self.secret_id))
        self.assertEqual(0, len(consumers))
