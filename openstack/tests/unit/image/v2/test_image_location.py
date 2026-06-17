# Copyright 2026 Red Hat Inc.
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from openstack.image.v2 import image_location
from openstack.tests.unit import base

EXAMPLE = {
    'image_id': '2',
    'url': 'http://spam.com/',
    'validation_data': {'os_hash_algo': 'sha512'},
    'metadata': {},
}


class TestImageLocation(base.TestCase):
    def test_basic(self):
        sot = image_location.ImageLocation()
        self.assertEqual('/images/%(image_id)s/locations', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = image_location.ImageLocation(**EXAMPLE)
        self.assertEqual(EXAMPLE['image_id'], sot.image_id)
        self.assertEqual(EXAMPLE['url'], sot.url)
        self.assertEqual(EXAMPLE['validation_data'], sot.validation_data)
        self.assertEqual(EXAMPLE['metadata'], sot.metadata)

    def test_prepare_request_body_includes_validation_data(self):
        sot = image_location.ImageLocation(
            image_id='test_id',
            url='http://spam.com/',
            validation_data={'os_hash_algo': 'sha512'},
        )
        body = sot._prepare_request_body(prepend_key=False)
        self.assertEqual(
            {
                'url': 'http://spam.com/',
                'validation_data': {'os_hash_algo': 'sha512'},
            },
            body,
        )
