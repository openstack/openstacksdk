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

from openstack import exceptions
from openstack.image.v2 import cache
from openstack.tests.unit import base


EXAMPLE = {
    'cached_images': [
        {
            'hits': 0,
            'image_id': '1a56983c-f71f-490b-a7ac-6b321a18935a',
            'last_accessed': 1671699579.444378,
            'last_modified': 1671699579.444378,
            'size': 0,
        },
    ],
    'queued_images': [
        '3a4560a1-e585-443e-9b39-553b46ec92d1',
        '6f99bf80-2ee6-47cf-acfe-1f1fabb7e810',
    ],
}


class TestCache(base.TestCase):
    def test_basic(self):
        sot = cache.Cache()
        self.assertIsNone(sot.resource_key)
        self.assertEqual('/cache', sot.base_path)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)

    def test_make_it(self):
        sot = cache.Cache(**EXAMPLE)
        self.assertEqual(
            [cache.CachedImage(**e) for e in EXAMPLE['cached_images']],
            sot.cached_images,
        )
        self.assertEqual(EXAMPLE['queued_images'], sot.queued_images)

    @mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
    def test_queue(self):
        sot = cache.Cache()
        sess = mock.Mock()
        sess.put = mock.Mock()
        sess.default_microversion = '2.14'

        sot.queue(sess, image='image_id')

        sess.put.assert_called_with(
            'cache/image_id', microversion=sess.default_microversion
        )

    @mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
    def test_clear(self):
        sot = cache.Cache(**EXAMPLE)
        session = mock.Mock()
        session.delete = mock.Mock()

        sot.clear(session)
        session.delete.assert_called_with('/cache', headers={})

        sot.clear(session, 'both')
        session.delete.assert_called_with('/cache', headers={})

        sot.clear(session, 'cache')
        session.delete.assert_called_with(
            '/cache', headers={'x-image-cache-clear-target': 'cache'}
        )

        sot.clear(session, 'queue')
        session.delete.assert_called_with(
            '/cache', headers={'x-image-cache-clear-target': 'queue'}
        )

        self.assertRaises(
            exceptions.InvalidRequest, sot.clear, session, 'invalid'
        )
