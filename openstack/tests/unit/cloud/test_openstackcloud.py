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
from openstack import proxy
from openstack import resource
from openstack.tests.unit import base


class TestSearch(base.TestCase):
    class FakeResource(resource.Resource):
        allow_fetch = True
        allow_list = True

        foo = resource.Body("foo")

    def setUp(self):
        super().setUp()

        self.session = proxy.Proxy(self.cloud)
        self.session._sdk_connection = self.cloud
        self.session._get = mock.Mock()
        self.session._list = mock.Mock()
        self.session._resource_registry = dict(fake=self.FakeResource)
        # Set the mock into the cloud connection
        setattr(self.cloud, "mock_session", self.session)

    def test_raises_unknown_service(self):
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.search_resources,
            "wrong_service.wrong_resource",
            "name",
        )

    def test_raises_unknown_resource(self):
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.search_resources,
            "mock_session.wrong_resource",
            "name",
        )

    def test_search_resources_get_finds(self):
        self.session._get.return_value = self.FakeResource(foo="bar")

        ret = self.cloud.search_resources("mock_session.fake", "fake_name")
        self.session._get.assert_called_with(self.FakeResource, "fake_name")

        self.assertEqual(1, len(ret))
        self.assertEqual(
            self.FakeResource(foo="bar").to_dict(), ret[0].to_dict()
        )

    def test_search_resources_list(self):
        self.session._get.side_effect = exceptions.NotFoundException
        self.session._list.return_value = [self.FakeResource(foo="bar")]

        ret = self.cloud.search_resources("mock_session.fake", "fake_name")
        self.session._get.assert_called_with(self.FakeResource, "fake_name")
        self.session._list.assert_called_with(
            self.FakeResource, name="fake_name"
        )

        self.assertEqual(1, len(ret))
        self.assertEqual(
            self.FakeResource(foo="bar").to_dict(), ret[0].to_dict()
        )

    def test_search_resources_args(self):
        self.session._get.side_effect = exceptions.NotFoundException
        self.session._list.return_value = []

        self.cloud.search_resources(
            "mock_session.fake",
            "fake_name",
            get_args=["getarg1"],
            get_kwargs={"getkwarg1": "1"},
            list_args=["listarg1"],
            list_kwargs={"listkwarg1": "1"},
            filter1="foo",
        )
        self.session._get.assert_called_with(
            self.FakeResource, "fake_name", "getarg1", getkwarg1="1"
        )
        self.session._list.assert_called_with(
            self.FakeResource,
            "listarg1",
            listkwarg1="1",
            name="fake_name",
            filter1="foo",
        )

    def test_search_resources_name_empty(self):
        self.session._list.return_value = [self.FakeResource(foo="bar")]

        ret = self.cloud.search_resources("mock_session.fake", None, foo="bar")
        self.session._get.assert_not_called()
        self.session._list.assert_called_with(self.FakeResource, foo="bar")

        self.assertEqual(1, len(ret))
        self.assertEqual(
            self.FakeResource(foo="bar").to_dict(), ret[0].to_dict()
        )
