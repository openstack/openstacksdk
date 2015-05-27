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

import testtools

from openstack.image import image_service
from openstack import session


class TestSession(testtools.TestCase):

    def test_parse_url(self):
        filt = image_service.ImageService()
        self.assertEqual(
            "http://127.0.0.1:9292/v1",
            session.parse_url(filt, "http://127.0.0.1:9292"))
        self.assertEqual(
            "http://127.0.0.1:9292/v2",
            session.parse_url(filt, "http://127.0.0.1:9292/v2.0"))
        filt.version = 'v1'
        self.assertEqual(
            "http://127.0.0.1:9292/v1/mytenant",
            session.parse_url(filt, "http://127.0.0.1:9292/v2.0/mytenant/"))
        self.assertEqual(
            "http://127.0.0.1:9292/wot/v1/mytenant",
            session.parse_url(filt, "http://127.0.0.1:9292/wot/v2.0/mytenant"))
