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

import httpretty
import mock
import six

from openstack.object_store.v1 import _proxy
from openstack.object_store.v1 import container
from openstack.object_store.v1 import obj
from openstack import session
from openstack.tests import base
from openstack.tests import fakes
from openstack.tests import test_proxy_base
from openstack import transport


class TestObjectStoreProxy(test_proxy_base.TestProxyBase):

    def setUp(self):
        super(TestObjectStoreProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)


class Test_account_metadata(TestObjectStoreProxy):

    @mock.patch("openstack.resource.Resource")
    def test_get_account_metadata(self, mock_resource):
        cont = container.Container()
        mock_resource = mock.MagicMock()
        mock_resource.head.return_value = cont

        result = self.proxy.get_account_metadata()

        self.assertEqual(result, cont)

    def test_set_account_metadata(self):
        container = mock.MagicMock()
        container.update.return_value = container

        result = self.proxy.set_account_metadata(container)

        self.assertIs(result, None)

        container.update.assert_called_once_with(self.session)

    @mock.patch("openstack.object_store.v1._proxy._container.Container")
    def test_get_account_metadata_no_arg(self, mock_container):
        created_container = mock.MagicMock()
        mock_container.return_value = created_container

        self.proxy.get_account_metadata()

        mock_container.assert_called_once_with()
        created_container.head.assert_called_once_with(self.session)


class Test_containers(TestObjectStoreProxy, base.TestTransportBase):

    TEST_URL = fakes.FakeAuthenticator.ENDPOINT

    def setUp(self):
        super(Test_containers, self).setUp()
        self.transport = transport.Transport(accept=transport.JSON)
        self.auth = fakes.FakeAuthenticator()
        self.session = session.Session(self.transport, self.auth)

        self.proxy = _proxy.Proxy(self.session)

        self.containers_body = []
        for i in range(3):
            self.containers_body.append({six.text_type("name"):
                                         six.text_type("container%d" % i)})

    @httpretty.activate
    def test_all_containers(self):
        self.stub_url(httpretty.GET,
                      path=[container.Container.base_path],
                      responses=[httpretty.Response(
                                 body=json.dumps(self.containers_body),
                                 status=200, content_type="application/json"),
                                 httpretty.Response(body=json.dumps([]),
                                 status=200, content_type="application/json")])

        count = 0
        for actual, expected in zip(self.proxy.containers(),
                                    self.containers_body):
            self.assertEqual(actual, expected)
            count += 1
        self.assertEqual(count, len(self.containers_body))

    @httpretty.activate
    def test_containers_limited(self):
        limit = len(self.containers_body) + 1
        limit_param = "?limit=%d" % limit

        self.stub_url(httpretty.GET,
                      path=[container.Container.base_path + limit_param],
                      json=self.containers_body)

        count = 0
        for actual, expected in zip(self.proxy.containers(limit=limit),
                                    self.containers_body):
            self.assertEqual(actual, expected)
            count += 1

        self.assertEqual(count, len(self.containers_body))
        # Since we've chosen a limit larger than the body, only one request
        # should be made, so it should be the last one.
        self.assertIn(limit_param, httpretty.last_request().path)

    @httpretty.activate
    def test_containers_with_marker(self):
        marker = six.text_type("container2")
        marker_param = "?marker=%s" % marker

        self.stub_url(httpretty.GET,
                      path=[container.Container.base_path + marker_param],
                      json=self.containers_body)

        count = 0
        for actual, expected in zip(self.proxy.containers(marker=marker),
                                    self.containers_body):
            # Make sure the marker made it into the actual request.
            self.assertIn(marker_param, httpretty.last_request().path)
            self.assertEqual(actual, expected)
            count += 1

        self.assertEqual(count, len(self.containers_body))

        # Since we have to make one request beyond the end, because no
        # limit was provided, make sure the last container appears as
        # the marker in this last request.
        self.assertIn(self.containers_body[-1]["name"],
                      httpretty.last_request().path)


class Test_container_metadata(TestObjectStoreProxy):

    @mock.patch("openstack.resource.Resource.from_id")
    def test_get_container_metadata_object(self, mock_fi):
        container = mock.MagicMock()
        container.name = "test"
        container.head.return_value = container
        mock_fi.return_value = container

        result = self.proxy.get_container_metadata(container)

        self.assertIs(result, container)
        container.head.assert_called_once_with(self.session)

    @mock.patch("openstack.resource.Resource.from_id")
    def test_get_container_metadata_name(self, mock_fi):
        name = six.text_type("my_container")
        created_container = mock.MagicMock()
        created_container.name = name
        created_container.head.return_value = created_container
        mock_fi.return_value = created_container

        result = self.proxy.get_container_metadata(name)

        self.assertEqual(result.name, name)
        created_container.head.assert_called_once_with(self.session)

    def test_set_container_metadata_object(self):
        container = mock.MagicMock()

        result = self.proxy.set_container_metadata(container)

        self.assertIsNone(result)
        container.create.assert_called_once_with(self.session)


class Test_create_container(TestObjectStoreProxy):

    @mock.patch("openstack.resource.Resource.from_id")
    def test_container_object(self, mock_fi):
        container = mock.MagicMock()
        container.create.return_value = container
        mock_fi.return_value = container

        result = self.proxy.create_container(container)

        self.assertIs(result, container)
        container.create.assert_called_once_with(self.session)

    @mock.patch("openstack.resource.Resource.from_id")
    def test_container_name(self, mock_fi):
        name = six.text_type("my_container")
        created_container = mock.MagicMock()
        created_container.name = name
        created_container.create.return_value = created_container
        mock_fi.return_value = created_container

        result = self.proxy.create_container(name)

        self.assertEqual(result.name, name)
        created_container.create.assert_called_once_with(self.session)


class Test_delete_container(TestObjectStoreProxy):

    @mock.patch("openstack.resource.Resource.from_id")
    def test_container_object(self, mock_fi):
        container = mock.MagicMock()
        mock_fi.return_value = container

        result = self.proxy.delete_container(container)

        self.assertIsNone(result)
        container.delete.assert_called_once_with(self.session)

    @mock.patch("openstack.resource.Resource.from_id")
    def test_container_name(self, mock_fi):
        name = six.text_type("my_container")
        created_container = mock.MagicMock()
        created_container.name = name
        mock_fi.return_value = created_container

        result = self.proxy.delete_container(name)

        self.assertIsNone(result)
        created_container.delete.assert_called_once_with(self.session)


class Test_objects(TestObjectStoreProxy, base.TestTransportBase):

    TEST_URL = fakes.FakeAuthenticator.ENDPOINT

    def setUp(self):
        super(Test_objects, self).setUp()
        self.transport = transport.Transport(accept=transport.JSON)
        self.auth = fakes.FakeAuthenticator()
        self.session = session.Session(self.transport, self.auth)

        self.proxy = _proxy.Proxy(self.session)

        self.container_name = six.text_type("my_container")

        self.objects_body = []
        for i in range(3):
            self.objects_body.append({six.text_type("name"):
                                      six.text_type("object%d" % i)})

        # Returned object bodies have their container inserted.
        self.returned_objects = []
        for ob in self.objects_body:
            ob[six.text_type("container")] = self.container_name
            self.returned_objects.append(ob)
        self.assertEqual(len(self.objects_body), len(self.returned_objects))

    @httpretty.activate
    def test_all_objects(self):
        self.stub_url(httpretty.GET,
                      path=[obj.Object.base_path %
                            {"container": self.container_name}],
                      responses=[httpretty.Response(
                                 body=json.dumps(self.objects_body),
                                 status=200, content_type="application/json"),
                                 httpretty.Response(body=json.dumps([]),
                                 status=200, content_type="application/json")])

        count = 0
        for actual, expected in zip(self.proxy.objects(self.container_name),
                                    self.returned_objects):
            self.assertEqual(actual, expected)
            count += 1
        self.assertEqual(count, len(self.returned_objects))

    @httpretty.activate
    def test_objects_limited(self):
        limit = len(self.objects_body) + 1
        limit_param = "?limit=%d" % limit

        self.stub_url(httpretty.GET,
                      path=[obj.Object.base_path %
                            {"container": self.container_name} + limit_param],
                      json=self.objects_body)

        count = 0
        for actual, expected in zip(self.proxy.objects(self.container_name,
                                                       limit=limit),
                                    self.returned_objects):
            self.assertEqual(actual, expected)
            count += 1

        self.assertEqual(count, len(self.returned_objects))
        # Since we've chosen a limit larger than the body, only one request
        # should be made, so it should be the last one.
        self.assertIn(limit_param, httpretty.last_request().path)

    @httpretty.activate
    def test_objects_with_marker(self):
        marker = six.text_type("object2")
        marker_param = "?marker=%s" % marker

        self.stub_url(httpretty.GET,
                      path=[obj.Object.base_path %
                            {"container": self.container_name} + marker_param],
                      json=self.objects_body)

        count = 0
        for actual, expected in zip(self.proxy.objects(self.container_name,
                                                       marker=marker),
                                    self.returned_objects):
            # Make sure the marker made it into the actual request.
            self.assertIn(marker_param, httpretty.last_request().path)
            self.assertEqual(actual, expected)
            count += 1

        self.assertEqual(count, len(self.returned_objects))

        # Since we have to make one request beyond the end, because no
        # limit was provided, make sure the last container appears as
        # the marker in this last request.
        self.assertIn(self.returned_objects[-1]["name"],
                      httpretty.last_request().path)


class Test_get_object_data(TestObjectStoreProxy):

    def test_get(self):
        the_data = "here's some data"
        ob = mock.MagicMock()
        ob.get.return_value = the_data

        result = self.proxy.get_object_data(ob)

        self.assertEqual(result, the_data)
        ob.get.assert_called_once_with(self.session)


class Test_save_object(TestObjectStoreProxy):

    @mock.patch("openstack.object_store.v1._proxy.Proxy.get_object_data")
    def test_save(self, mock_get):
        the_data = "here's some data"
        mock_get.return_value = the_data
        ob = mock.MagicMock()

        fake_open = mock.mock_open()
        file_path = "blarga/somefile"
        with mock.patch("openstack.object_store.v1._proxy.open",
                        fake_open, create=True):
            self.proxy.save_object(ob, file_path)

        fake_open.assert_called_once_with(file_path, "w")
        fake_handle = fake_open()
        fake_handle.write.assert_called_once_with(the_data)


class Test_create_object(TestObjectStoreProxy):

    def setUp(self):
        super(Test_create_object, self).setUp()
        self.the_data = six.b("here's some data")
        self.container_name = six.text_type("my_container")
        self.object_name = six.text_type("my_object")

    @mock.patch("openstack.object_store.v1.obj.Object.from_id")
    def test_create_with_obj_name_real_container(self, mock_fi):
        created_object = mock.MagicMock()
        created_object.name = self.object_name
        created_object.create.return_value = created_object
        # Since we're using a MagicMock, we have to explicitly set this to
        # None otherwise when it gets accessed it'll have a value which
        # is not what we want to happen.
        created_object.container = None
        mock_fi.return_value = created_object

        cont = container.Container.new(name=self.container_name)

        result = self.proxy.create_object(self.the_data, self.object_name,
                                          cont)

        self.assertIs(result, created_object)
        self.assertEqual(result.name, self.object_name)
        self.assertEqual(result.container, self.container_name)
        created_object.create.assert_called_once_with(self.session,
                                                      self.the_data)

    def test_create_with_real_obj_real_container(self):
        ob = obj.Object.new(name=self.object_name)
        ob.create = mock.MagicMock()
        ob.create.return_value = ob
        cont = container.Container.new(name=self.container_name)

        result = self.proxy.create_object(self.the_data, ob, cont)

        self.assertIs(result, ob)
        self.assertEqual(result.name, self.object_name)
        self.assertEqual(result.container, self.container_name)
        ob.create.assert_called_once_with(self.session, self.the_data)

    def test_create_with_full_obj_no_container_arg(self):
        ob = obj.Object.new(name=self.object_name,
                            container=self.container_name)
        ob.create = mock.MagicMock()
        ob.create.return_value = ob

        result = self.proxy.create_object(self.the_data, ob)

        self.assertIs(result, ob)
        self.assertEqual(result.name, self.object_name)
        self.assertEqual(result.container, self.container_name)
        ob.create.assert_called_once_with(self.session, self.the_data)


class Test_object_metadata(TestObjectStoreProxy):

    @mock.patch("openstack.resource.Resource.from_id")
    def test_get_object_metadata(self, mock_fi):
        ob = mock.MagicMock()
        ob.head.return_value = ob
        mock_fi.return_value = ob

        result = self.proxy.get_object_metadata(ob)

        self.assertIs(result, ob)
        ob.head.assert_called_once_with(self.session)

    def test_set_object_metadata(self):
        ob = mock.MagicMock()

        result = self.proxy.set_object_metadata(ob)

        self.assertIsNone(result)
        ob.create.assert_called_once_with(self.session)


class Test_delete_object(TestObjectStoreProxy):

    def test_delete_object(self):
        ob = mock.MagicMock()

        result = self.proxy.delete_object(ob)

        self.assertIsNone(result)
        ob.delete.assert_called_once_with(self.session)


class Test_copy_object(TestObjectStoreProxy):

    def test_copy_object(self):
        self.assertRaises(NotImplementedError, self.proxy.copy_object)
