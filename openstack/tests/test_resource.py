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

import httpretty

from openstack import resource
from openstack import session
from openstack.tests import base
from openstack.tests import fakes
from openstack import transport

fake_name = 'name'
fake_id = 99
fake_attr1 = 'attr1'
fake_attr2 = 'attr2'

fake_resource = 'fake'
fake_resources = 'fakes'
fake_path = fake_resources

fake_data = {'id': fake_id,
             'name': fake_name,
             'attr1': fake_attr1,
             'attr2': fake_attr2}
fake_body = {fake_resource: fake_data}


class FakeResource(resource.Resource):

    resource_key = fake_resource
    resources_key = fake_path
    base_path = '/%s' % fake_path

    allow_create = allow_retrieve = allow_update = True
    allow_delete = allow_list = True


class ResourceTests(base.TestTransportBase):

    TEST_URL = fakes.FakeAuthenticator.ENDPOINT

    def setUp(self):
        super(ResourceTests, self).setUp()
        self.transport = transport.Transport()
        self.auth = fakes.FakeAuthenticator()
        self.session = session.Session(self.transport, self.auth)

    @httpretty.activate
    def test_create(self):
        self.stub_url(httpretty.POST, path=fake_path, json=fake_body)

        obj = FakeResource.new(name=fake_name,
                               attr1=fake_attr1, attr2=fake_attr2)
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

    @httpretty.activate
    def test_get(self):
        self.stub_url(httpretty.GET, path=[fake_path, fake_id], json=fake_body)
        obj = FakeResource.get_by_id(self.session, fake_id)

        self.assertEqual(fake_name, obj['name'])
        self.assertEqual(fake_id, obj.id)
        self.assertEqual(fake_attr1, obj['attr1'])
        self.assertEqual(fake_attr2, obj['attr2'])

    @httpretty.activate
    def test_update(self):
        new_attr1 = 'attr5'
        fake_body1 = fake_body.copy()
        fake_body1[fake_resource]['attr1'] = new_attr1

        self.stub_url(httpretty.POST, path=fake_path, json=fake_body1)
        self.stub_url(httpretty.PATCH,
                      path=[fake_path, fake_id],
                      json=fake_body)

        obj = FakeResource.new(name=fake_name,
                               attr1=new_attr1,
                               attr2=fake_attr2)
        obj.create(self.session)
        self.assertFalse(obj.is_dirty)
        self.assertEqual(new_attr1, obj['attr1'])

        obj['attr1'] = fake_attr1
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

    @httpretty.activate
    def test_delete(self):
        self.stub_url(httpretty.GET, path=[fake_path, fake_id], json=fake_body)
        self.stub_url(httpretty.DELETE, [fake_path, fake_id])
        obj = FakeResource.get_by_id(self.session, fake_id)

        obj.delete(self.session)

        last_req = httpretty.last_request()
        self.assertEqual('DELETE', last_req.method)
        self.assertEqual('/endpoint/%s/%s' % (fake_path, fake_id),
                         last_req.path)

    @httpretty.activate
    def test_list(self):
        results = [fake_data.copy(), fake_data.copy(), fake_data.copy()]
        for i in range(len(results)):
            results[i]['id'] = fake_id + i

        self.stub_url(httpretty.GET,
                      path=fake_path,
                      json={fake_resources: results})

        objs = FakeResource.list(self.session, marker='x')

        self.assertIn('marker=x', httpretty.last_request().path)
        self.assertEqual(3, len(objs))

        for obj in objs:
            self.assertIn(obj.id, range(fake_id, fake_id + 3))
            self.assertEqual(fake_name, obj['name'])
            self.assertIsInstance(obj, FakeResource)
