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

import copy

import httpretty
import mock

from openstack import exceptions
from openstack import resource
from openstack import session
from openstack.tests import base
from openstack.tests import fakes
from openstack import transport

fake_name = 'rey'
fake_id = 99
fake_attr1 = 'lana'
fake_attr2 = 'del'

fake_resource = 'fake'
fake_resources = 'fakes'
fake_arguments = {'name': 'rey'}
fake_base_path = '/fakes/%(name)s/data'
fake_path = '/fakes/rey/data'

fake_data = {'id': fake_id,
             'name': fake_name,
             'attr1': fake_attr1,
             'attr2': fake_attr2}
fake_body = {fake_resource: fake_data}


class FakeResource(resource.Resource):

    resource_key = fake_resource
    resources_key = fake_resources
    base_path = fake_base_path

    allow_create = allow_retrieve = allow_update = True
    allow_delete = allow_list = allow_head = True

    name = resource.prop('name')
    first = resource.prop('attr1')
    second = resource.prop('attr2')
    third = resource.prop('attr3', alias='attr_three')


class ResourceTests(base.TestTransportBase):

    TEST_URL = fakes.FakeAuthenticator.ENDPOINT

    def setUp(self):
        super(ResourceTests, self).setUp()
        self.transport = transport.Transport(accept=transport.JSON)
        self.auth = fakes.FakeAuthenticator()
        self.session = session.Session(self.transport, self.auth)

    @httpretty.activate
    def test_empty_id(self):
        self.stub_url(httpretty.GET, path=[fake_path], json=fake_body)
        obj = FakeResource.new(**fake_arguments)
        obj.get(self.session)

        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)

    @httpretty.activate
    def test_create(self):
        self.stub_url(httpretty.POST, path=fake_path, json=fake_body)

        obj = FakeResource.new(name=fake_name,
                               attr1=fake_attr1,
                               attr2=fake_attr2)

        obj.create(self.session)
        self.assertFalse(obj.is_dirty)

        last_req = httpretty.last_request().parsed_body[fake_resource]

        self.assertEqual(3, len(last_req))
        self.assertEqual(fake_name, last_req['name'])
        self.assertEqual(fake_attr1, last_req['attr1'])
        self.assertEqual(fake_attr2, last_req['attr2'])

        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)

    @httpretty.activate
    def test_get(self):
        self.stub_url(httpretty.GET, path=[fake_path, fake_id], json=fake_body)
        obj = FakeResource.get_by_id(self.session, fake_id,
                                     path_args=fake_arguments)

        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)

    @httpretty.activate
    def test_head(self):
        self.stub_url(httpretty.HEAD, path=[fake_path, fake_id],
                      name=fake_name,
                      attr1=fake_attr1,
                      attr2=fake_attr2)
        obj = FakeResource.head_by_id(self.session, fake_id,
                                      path_args=fake_arguments)

        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)

    @httpretty.activate
    def test_update(self):
        new_attr1 = 'attr5'
        new_attr2 = 'attr6'
        fake_body1 = copy.deepcopy(fake_body)
        fake_body1[fake_resource]['attr1'] = new_attr1

        self.stub_url(httpretty.POST, path=fake_path, json=fake_body1)
        self.stub_url(httpretty.PATCH,
                      path=[fake_path, fake_id],
                      json=fake_body)

        obj = FakeResource.new(name=fake_name,
                               attr1=new_attr1,
                               attr2=new_attr2)
        obj.create(self.session)
        self.assertFalse(obj.is_dirty)
        self.assertEqual(new_attr1, obj['attr1'])

        obj['attr1'] = fake_attr1
        obj.second = fake_attr2
        self.assertTrue(obj.is_dirty)

        obj.update(self.session)
        self.assertFalse(obj.is_dirty)

        last_req = httpretty.last_request().parsed_body[fake_resource]
        self.assertEqual(1, len(last_req))
        self.assertEqual(fake_attr1, last_req['attr1'])

        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

        self.assertEqual(fake_name, obj.name)
        self.assertEqual(fake_attr1, obj.first)
        self.assertEqual(fake_attr2, obj.second)

    @httpretty.activate
    def test_delete(self):
        self.stub_url(httpretty.GET, path=[fake_path, fake_id], json=fake_body)
        self.stub_url(httpretty.DELETE, [fake_path, fake_id])
        obj = FakeResource.get_by_id(self.session, fake_id,
                                     path_args=fake_arguments)

        obj.delete(self.session)

        last_req = httpretty.last_request()
        self.assertEqual('DELETE', last_req.method)
        self.assertEqual('/endpoint/fakes/rey/data/99', last_req.path)

    @httpretty.activate
    def test_list(self):
        results = [fake_data.copy(), fake_data.copy(), fake_data.copy()]
        for i in range(len(results)):
            results[i]['id'] = fake_id + i

        self.stub_url(httpretty.GET,
                      path=[fake_path],
                      json={fake_resources: results})

        objs = FakeResource.list(self.session, marker='x',
                                 path_args=fake_arguments)

        self.assertIn('marker=x', httpretty.last_request().path)
        self.assertEqual(3, len(objs))

        for obj in objs:
            self.assertIn(obj.id, range(fake_id, fake_id + 3))
            self.assertEqual(fake_name, obj['name'])
            self.assertEqual(fake_name, obj.name)
            self.assertIsInstance(obj, FakeResource)

    def test_attrs(self):
        obj = FakeResource()

        try:
            obj.name
        except AttributeError:
            pass
        else:
            self.fail("Didn't raise attribute error")

        try:
            del obj.name
        except AttributeError:
            pass
        else:
            self.fail("Didn't raise attribute error")

        try:
            obj.third
        except AttributeError:
            pass
        else:
            self.fail("Didn't raise attribute error")

    def test_composite_attr_happy(self):
        obj = FakeResource.existing(**{'attr3': '3'})

        try:
            self.assertEqual('3', obj.third)
        except AttributeError:
            self.fail("third was not found as expected")

    def test_composite_attr_fallback(self):
        obj = FakeResource.existing(**{'attr_three': '3'})

        try:
            self.assertEqual('3', obj.third)
        except AttributeError:
            self.fail("third was not found in fallback as expected")


class FakeResponse:
    def __init__(self, response):
        self.body = response


class TestFind(base.TestCase):
    NAME = 'matrix'
    ID = 'Fishburne'

    def setUp(self):
        super(TestFind, self).setUp()
        self.mock_session = mock.Mock()
        self.mock_get = mock.Mock()
        self.mock_session.get = self.mock_get
        self.matrix = {'id': self.ID}

    def test_name(self):
        self.mock_get.side_effect = [
            FakeResponse({FakeResource.resources_key: []}),
            FakeResponse({FakeResource.resources_key: [self.matrix]})
        ]

        result = FakeResource.find(self.mock_session, self.NAME,
                                   path_args=fake_arguments)

        self.assertEqual(self.ID, result.id)
        p = {'fields': 'id', 'name': self.NAME}
        self.mock_get.assert_called_with(fake_path, params=p, service=None)

    def test_id(self):
        resp = FakeResponse({FakeResource.resources_key: [self.matrix]})
        self.mock_get.return_value = resp

        result = FakeResource.find(self.mock_session, self.ID,
                                   path_args=fake_arguments)

        self.assertEqual(self.ID, result.id)
        p = {'fields': 'id', 'id': self.ID}
        self.mock_get.assert_called_with(fake_path, params=p, service=None)

    def test_nameo(self):
        self.mock_get.side_effect = [
            FakeResponse({FakeResource.resources_key: []}),
            FakeResponse({FakeResource.resources_key: [self.matrix]})
        ]
        FakeResource.name_attribute = 'nameo'

        result = FakeResource.find(self.mock_session, self.NAME,
                                   path_args=fake_arguments)

        FakeResource.name_attribute = 'name'
        self.assertEqual(self.ID, result.id)
        p = {'fields': 'id', 'nameo': self.NAME}
        self.mock_get.assert_called_with(fake_path, params=p, service=None)

    def test_dups(self):
        dup = {'id': 'Larry'}
        resp = FakeResponse({FakeResource.resources_key: [self.matrix, dup]})
        self.mock_get.return_value = resp

        self.assertRaises(exceptions.DuplicateResource, FakeResource.find,
                          self.mock_session, self.NAME)

    def test_id_attribute_find(self):
        floater = {'ip_address': "127.0.0.1"}
        resp = FakeResponse({FakeResource.resources_key: [floater]})
        self.mock_get.return_value = resp

        FakeResource.id_attribute = 'ip_address'
        result = FakeResource.find(self.mock_session, "127.0.0.1",
                                   path_args=fake_arguments)
        self.assertEqual("127.0.0.1", result.id)
        FakeResource.id_attribute = 'id'

        p = {'fields': 'ip_address', 'ip_address': "127.0.0.1"}
        self.mock_get.assert_called_with(fake_path, params=p, service=None)

    def test_nada(self):
        resp = FakeResponse({FakeResource.resources_key: []})
        self.mock_get.return_value = resp

        self.assertRaises(exceptions.ResourceNotFound, FakeResource.find,
                          self.mock_session, self.NAME)

    def test_no_name(self):
        self.mock_get.side_effect = [
            FakeResponse({FakeResource.resources_key: []}),
            FakeResponse({FakeResource.resources_key: [self.matrix]})
        ]
        FakeResource.name_attribute = None

        self.assertRaises(exceptions.ResourceNotFound, FakeResource.find,
                          self.mock_session, self.NAME)

    def test_repr_name(self):
        FakeResource.resource_name = 'foo'
        self.assertEqual('foo: {}', repr(FakeResource()))
        FakeResource.resource_name = None
        FakeResource.resource_key = None
        self.assertEqual('FakeResource: {}', repr(FakeResource()))
        FakeResource.resource_key = fake_resource
        self.assertEqual(fake_resource + ': {}', repr(FakeResource()))

    def test_id_attribute(self):
        faker = FakeResource(fake_data)
        self.assertEqual(fake_id, faker.id)
        faker.id_attribute = 'name'
        self.assertEqual(fake_name, faker.id)
        faker.id_attribute = 'attr1'
        self.assertEqual(fake_attr1, faker.id)
        faker.id_attribute = 'attr2'
        self.assertEqual(fake_attr2, faker.id)
        faker.id_attribute = 'id'
        self.assertEqual(fake_id, faker.id)
