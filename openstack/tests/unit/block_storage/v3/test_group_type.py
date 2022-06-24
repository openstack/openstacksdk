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

from openstack.block_storage.v3 import group_type
from openstack.tests.unit import base

GROUP_TYPE = {
    "id": "6685584b-1eac-4da6-b5c3-555430cf68ff",
    "name": "grp-type-001",
    "description": "group type 001",
    "is_public": True,
    "group_specs": {"consistent_group_snapshot_enabled": "<is> False"},
}


class TestGroupType(base.TestCase):
    def setUp(self):
        super().setUp()
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.default_microversion = 1
        self.sess._get_connection = mock.Mock(return_value=self.cloud)

    def test_basic(self):
        resource = group_type.GroupType()
        self.assertEqual("group_type", resource.resource_key)
        self.assertEqual("group_types", resource.resources_key)
        self.assertEqual("/group_types", resource.base_path)
        self.assertTrue(resource.allow_create)
        self.assertTrue(resource.allow_fetch)
        self.assertTrue(resource.allow_delete)
        self.assertTrue(resource.allow_commit)
        self.assertTrue(resource.allow_list)

    def test_make_resource(self):
        resource = group_type.GroupType(**GROUP_TYPE)
        self.assertEqual(GROUP_TYPE["id"], resource.id)
        self.assertEqual(GROUP_TYPE["name"], resource.name)
        self.assertEqual(GROUP_TYPE["description"], resource.description)
        self.assertEqual(GROUP_TYPE["is_public"], resource.is_public)
        self.assertEqual(GROUP_TYPE["group_specs"], resource.group_specs)

    def test_fetch_group_specs(self):
        sot = group_type.GroupType(**GROUP_TYPE)
        resp = mock.Mock()
        resp.body = {'group_specs': {'a': 'b', 'c': 'd'}}
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.get = mock.Mock(return_value=resp)

        rsp = sot.fetch_group_specs(self.sess)

        self.sess.get.assert_called_with(
            f"group_types/{GROUP_TYPE['id']}/group_specs",
            microversion=self.sess.default_microversion,
        )

        self.assertEqual(resp.body['group_specs'], rsp.group_specs)
        self.assertIsInstance(rsp, group_type.GroupType)

    def test_create_group_specs(self):
        sot = group_type.GroupType(**GROUP_TYPE)
        specs = {'a': 'b', 'c': 'd'}
        resp = mock.Mock()
        resp.body = {'group_specs': specs}
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.post = mock.Mock(return_value=resp)

        rsp = sot.create_group_specs(self.sess, specs)

        self.sess.post.assert_called_with(
            f"group_types/{GROUP_TYPE['id']}/group_specs",
            json={'group_specs': specs},
            microversion=self.sess.default_microversion,
        )

        self.assertEqual(resp.body['group_specs'], rsp.group_specs)
        self.assertIsInstance(rsp, group_type.GroupType)

    def test_get_group_specs_property(self):
        sot = group_type.GroupType(**GROUP_TYPE)
        resp = mock.Mock()
        resp.body = {'a': 'b'}
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.get = mock.Mock(return_value=resp)

        rsp = sot.get_group_specs_property(self.sess, 'a')

        self.sess.get.assert_called_with(
            f"group_types/{GROUP_TYPE['id']}/group_specs/a",
            microversion=self.sess.default_microversion,
        )

        self.assertEqual('b', rsp)

    def test_update_group_specs_property(self):
        sot = group_type.GroupType(**GROUP_TYPE)
        resp = mock.Mock()
        resp.body = {'a': 'b'}
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.put = mock.Mock(return_value=resp)

        rsp = sot.update_group_specs_property(self.sess, 'a', 'b')

        self.sess.put.assert_called_with(
            f"group_types/{GROUP_TYPE['id']}/group_specs/a",
            json={'a': 'b'},
            microversion=self.sess.default_microversion,
        )

        self.assertEqual('b', rsp)

    def test_delete_group_specs_property(self):
        sot = group_type.GroupType(**GROUP_TYPE)
        resp = mock.Mock()
        resp.body = None
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.delete = mock.Mock(return_value=resp)

        rsp = sot.delete_group_specs_property(self.sess, 'a')

        self.sess.delete.assert_called_with(
            f"group_types/{GROUP_TYPE['id']}/group_specs/a",
            microversion=self.sess.default_microversion,
        )

        self.assertIsNone(rsp)
