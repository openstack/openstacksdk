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

from openstack.identity.v3 import group
from openstack.identity.v3 import project
from openstack.identity.v3 import role
from openstack.identity.v3 import user
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'description': '1',
    'domain_id': '2',
    'enabled': True,
    'id': IDENTIFIER,
    'is_domain': False,
    'links': {'self': f'http://example.com/identity/v3/projects/{IDENTIFIER}'},
    'name': '5',
    'parent_id': '6',
    'options': {'foo': 'bar'},
}


class TestProject(base.TestCase):
    def setUp(self):
        super().setUp()
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.default_microversion = 1
        self.sess._get_connection = mock.Mock(return_value=self.cloud)
        self.good_resp = mock.Mock()
        self.good_resp.body = None
        self.good_resp.json = mock.Mock(return_value=self.good_resp.body)
        self.good_resp.status_code = 204

        self.bad_resp = mock.Mock()
        self.bad_resp.body = None
        self.bad_resp.json = mock.Mock(return_value=self.bad_resp.body)
        self.bad_resp.status_code = 401

    def test_basic(self):
        sot = project.Project()
        self.assertEqual('project', sot.resource_key)
        self.assertEqual('projects', sot.resources_key)
        self.assertEqual('/projects', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertEqual('PATCH', sot.commit_method)

        self.assertDictEqual(
            {
                'domain_id': 'domain_id',
                'is_domain': 'is_domain',
                'name': 'name',
                'parent_id': 'parent_id',
                'is_enabled': 'enabled',
                'limit': 'limit',
                'marker': 'marker',
                'tags': 'tags',
                'any_tags': 'tags-any',
                'not_tags': 'not-tags',
                'not_any_tags': 'not-tags-any',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = project.Project(**EXAMPLE)
        self.assertEqual(EXAMPLE['description'], sot.description)
        self.assertEqual(EXAMPLE['domain_id'], sot.domain_id)
        self.assertFalse(sot.is_domain)
        self.assertTrue(sot.is_enabled)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['links'], sot.links)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['parent_id'], sot.parent_id)
        self.assertDictEqual(EXAMPLE['options'], sot.options)

    def test_assign_role_to_user_good(self):
        sot = project.Project(**EXAMPLE)
        resp = self.good_resp
        self.sess.put = mock.Mock(return_value=resp)

        self.assertTrue(
            sot.assign_role_to_user(
                self.sess, user.User(id='1'), role.Role(id='2'), False
            )
        )

        self.sess.put.assert_called_with('projects/IDENTIFIER/users/1/roles/2')

    def test_assign_inherited_role_to_user_good(self):
        sot = project.Project(**EXAMPLE)
        resp = self.good_resp
        self.sess.put = mock.Mock(return_value=resp)

        self.assertTrue(
            sot.assign_role_to_user(
                self.sess, user.User(id='1'), role.Role(id='2'), True
            )
        )

        self.sess.put.assert_called_with(
            'OS-INHERIT/projects/IDENTIFIER/users/1/roles/2/inherited_to_projects'
        )

    def test_assign_role_to_user_bad(self):
        sot = project.Project(**EXAMPLE)
        resp = self.bad_resp
        self.sess.put = mock.Mock(return_value=resp)

        self.assertFalse(
            sot.assign_role_to_user(
                self.sess, user.User(id='1'), role.Role(id='2'), False
            )
        )

    def test_validate_user_has_role_good(self):
        sot = project.Project(**EXAMPLE)
        resp = self.good_resp
        self.sess.head = mock.Mock(return_value=resp)

        self.assertTrue(
            sot.validate_user_has_role(
                self.sess, user.User(id='1'), role.Role(id='2'), False
            )
        )

        self.sess.head.assert_called_with(
            'projects/IDENTIFIER/users/1/roles/2'
        )

    def test_validate_user_has_inherited_role_good(self):
        sot = project.Project(**EXAMPLE)
        resp = self.good_resp
        self.sess.head = mock.Mock(return_value=resp)

        self.assertTrue(
            sot.validate_user_has_role(
                self.sess, user.User(id='1'), role.Role(id='2'), True
            )
        )

        self.sess.head.assert_called_with(
            'OS-INHERIT/projects/IDENTIFIER/users/1/roles/2/inherited_to_projects'
        )

    def test_validate_user_has_role_bad(self):
        sot = project.Project(**EXAMPLE)
        resp = self.bad_resp
        self.sess.head = mock.Mock(return_value=resp)

        self.assertFalse(
            sot.validate_user_has_role(
                self.sess, user.User(id='1'), role.Role(id='2'), False
            )
        )

    def test_unassign_role_from_user_good(self):
        sot = project.Project(**EXAMPLE)
        resp = self.good_resp
        self.sess.delete = mock.Mock(return_value=resp)

        self.assertTrue(
            sot.unassign_role_from_user(
                self.sess, user.User(id='1'), role.Role(id='2'), False
            )
        )

        self.sess.delete.assert_called_with(
            'projects/IDENTIFIER/users/1/roles/2'
        )

    def test_unassign_inherited_role_from_user_good(self):
        sot = project.Project(**EXAMPLE)
        resp = self.good_resp
        self.sess.delete = mock.Mock(return_value=resp)

        self.assertTrue(
            sot.unassign_role_from_user(
                self.sess, user.User(id='1'), role.Role(id='2'), True
            )
        )

        self.sess.delete.assert_called_with(
            'OS-INHERIT/projects/IDENTIFIER/users/1/roles/2/inherited_to_projects'
        )

    def test_unassign_role_from_user_bad(self):
        sot = project.Project(**EXAMPLE)
        resp = self.bad_resp
        self.sess.delete = mock.Mock(return_value=resp)

        self.assertFalse(
            sot.unassign_role_from_user(
                self.sess, user.User(id='1'), role.Role(id='2'), False
            )
        )

    def test_assign_role_to_group_good(self):
        sot = project.Project(**EXAMPLE)
        resp = self.good_resp
        self.sess.put = mock.Mock(return_value=resp)

        self.assertTrue(
            sot.assign_role_to_group(
                self.sess, group.Group(id='1'), role.Role(id='2'), False
            )
        )

        self.sess.put.assert_called_with(
            'projects/IDENTIFIER/groups/1/roles/2'
        )

    def test_assign_inherited_role_to_group_good(self):
        sot = project.Project(**EXAMPLE)
        resp = self.good_resp
        self.sess.put = mock.Mock(return_value=resp)

        self.assertTrue(
            sot.assign_role_to_group(
                self.sess, group.Group(id='1'), role.Role(id='2'), True
            )
        )

        self.sess.put.assert_called_with(
            'OS-INHERIT/projects/IDENTIFIER/groups/1/roles/2/inherited_to_projects'
        )

    def test_assign_role_to_group_bad(self):
        sot = project.Project(**EXAMPLE)
        resp = self.bad_resp
        self.sess.put = mock.Mock(return_value=resp)

        self.assertFalse(
            sot.assign_role_to_group(
                self.sess, group.Group(id='1'), role.Role(id='2'), False
            )
        )

    def test_validate_group_has_role_good(self):
        sot = project.Project(**EXAMPLE)
        resp = self.good_resp
        self.sess.head = mock.Mock(return_value=resp)

        self.assertTrue(
            sot.validate_group_has_role(
                self.sess, group.Group(id='1'), role.Role(id='2'), False
            )
        )

        self.sess.head.assert_called_with(
            'projects/IDENTIFIER/groups/1/roles/2'
        )

    def test_validate_group_has_inherited_role_good(self):
        sot = project.Project(**EXAMPLE)
        resp = self.good_resp
        self.sess.head = mock.Mock(return_value=resp)

        self.assertTrue(
            sot.validate_group_has_role(
                self.sess, group.Group(id='1'), role.Role(id='2'), True
            )
        )

        self.sess.head.assert_called_with(
            'OS-INHERIT/projects/IDENTIFIER/groups/1/roles/2/inherited_to_projects'
        )

    def test_validate_group_has_role_bad(self):
        sot = project.Project(**EXAMPLE)
        resp = self.bad_resp
        self.sess.head = mock.Mock(return_value=resp)

        self.assertFalse(
            sot.validate_group_has_role(
                self.sess, group.Group(id='1'), role.Role(id='2'), False
            )
        )

    def test_unassign_role_from_group_good(self):
        sot = project.Project(**EXAMPLE)
        resp = self.good_resp
        self.sess.delete = mock.Mock(return_value=resp)

        self.assertTrue(
            sot.unassign_role_from_group(
                self.sess, group.Group(id='1'), role.Role(id='2'), False
            )
        )

        self.sess.delete.assert_called_with(
            'projects/IDENTIFIER/groups/1/roles/2'
        )

    def test_unassign_inherited_role_from_group_good(self):
        sot = project.Project(**EXAMPLE)
        resp = self.good_resp
        self.sess.delete = mock.Mock(return_value=resp)

        self.assertTrue(
            sot.unassign_role_from_group(
                self.sess, group.Group(id='1'), role.Role(id='2'), True
            )
        )

        self.sess.delete.assert_called_with(
            'OS-INHERIT/projects/IDENTIFIER/groups/1/roles/2/inherited_to_projects'
        )

    def test_unassign_role_from_group_bad(self):
        sot = project.Project(**EXAMPLE)
        resp = self.bad_resp
        self.sess.delete = mock.Mock(return_value=resp)

        self.assertFalse(
            sot.unassign_role_from_group(
                self.sess, group.Group(id='1'), role.Role(id='2'), False
            )
        )


class TestUserProject(base.TestCase):
    def test_basic(self):
        sot = project.UserProject()
        self.assertEqual('project', sot.resource_key)
        self.assertEqual('projects', sot.resources_key)
        self.assertEqual('/users/%(user_id)s/projects', sot.base_path)
        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertTrue(sot.allow_list)
