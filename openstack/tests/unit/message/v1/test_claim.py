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

import json
import mock
import testtools

from openstack.message.v1 import claim

CLIENT = '3381af92-2b9e-11e3-b191-71861300734c'
QUEUE = 'test_queue'
LIMIT = 2
FAKE = {
    'ttl': 300,
    'grace': 60
}


class TestClaim(testtools.TestCase):

    def test_basic(self):
        sot = claim.Claim()
        self.assertEqual('claims', sot.resources_key)
        self.assertEqual('/queues/%(queue_name)s/claims', sot.base_path)
        self.assertEqual('messaging', sot.service.service_type)
        self.assertTrue(sot.allow_create)
        self.assertFalse(sot.allow_retrieve)
        self.assertFalse(sot.allow_update)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)

    def test_make_it(self):
        sot = claim.Claim.new(client=CLIENT, queue=QUEUE, limit=LIMIT, **FAKE)
        self.assertEqual(CLIENT, sot.client)
        self.assertEqual(QUEUE, sot.queue)
        self.assertEqual(LIMIT, sot.limit)
        self.assertEqual(FAKE['ttl'], sot.ttl)
        self.assertEqual(FAKE['grace'], sot.grace)

    def test_create(self):
        sess = mock.Mock()
        sess.post = mock.Mock()
        sess.post.return_value = mock.MagicMock()
        sot = claim.Claim()

        list(sot.claim_messages(
            sess, claim.Claim.new(client=CLIENT, queue=QUEUE, **FAKE)))

        url = '/queues/%s/claims' % QUEUE
        sess.post.assert_called_with(
            url, service=sot.service,
            headers={'Client-ID': CLIENT}, params=None,
            data=json.dumps(FAKE, cls=claim.ClaimEncoder))
