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

from openstack.baremetal.v1 import _common
from openstack.tests.unit import base


class FakeResource(_common.Resource):
    base_path = '/fakes'
    resources_key = 'fakes'
    allow_list = True


class TestResourceList(base.TestCase):
    def setUp(self):
        super().setUp()
        self.session = mock.Mock(spec=adapter.Adapter)
        self.session.default_microversion = None
        self.session.get.return_value.status_code = 200
        self.session.get.return_value.json.return_value = {'fakes': []}

    def test_list(self):
        self.assertEqual([], list(FakeResource.list(self.session)))
        self.assertEqual('/fakes', self.session.get.call_args[0][0])

    def test_list_details(self):
        self.assertEqual(
            [], list(FakeResource.list(self.session, details=True))
        )
        self.assertEqual('/fakes/detail', self.session.get.call_args[0][0])

    def test_list_details_explicit_base_path(self):
        self.assertEqual(
            [],
            list(
                FakeResource.list(
                    self.session, details=True, base_path='/other'
                )
            ),
        )
        self.assertEqual('/other', self.session.get.call_args[0][0])
