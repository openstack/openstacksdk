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

import pprint
import random
import string

from openstack import exceptions
from openstack.tests.functional import base
from openstack import utils


class TestDomain(base.KeystoneBaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        self.domain_prefix = self.getUniqueString('domain')
        self.addCleanup(self._cleanup_domains)

    def _cleanup_domains(self):
        exception_list = list()
        for domain in self.operator_cloud.list_domains():
            if domain['name'].startswith(self.domain_prefix):
                try:
                    self.operator_cloud.delete_domain(domain['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_search_domains(self):
        domain_name = self.domain_prefix + '_search'

        # Shouldn't find any domain with this name yet
        results = self.operator_cloud.search_domains(
            filters=dict(name=domain_name)
        )
        self.assertEqual(0, len(results))

        # Now create a new domain
        domain = self.operator_cloud.create_domain(domain_name)
        self.assertEqual(domain_name, domain['name'])

        # Now we should find only the new domain
        results = self.operator_cloud.search_domains(
            filters=dict(name=domain_name)
        )
        self.assertEqual(1, len(results))
        self.assertEqual(domain_name, results[0]['name'])

        # Now we search by name with name_or_id, should find only new domain
        results = self.operator_cloud.search_domains(name_or_id=domain_name)
        self.assertEqual(1, len(results))
        self.assertEqual(domain_name, results[0]['name'])

    def test_update_domain(self):
        domain = self.operator_cloud.create_domain(
            self.domain_prefix, 'description'
        )
        self.assertEqual(self.domain_prefix, domain['name'])
        self.assertEqual('description', domain['description'])
        self.assertTrue(domain['enabled'])
        updated = self.operator_cloud.update_domain(
            domain['id'],
            name='updated name',
            description='updated description',
            enabled=False,
        )
        self.assertEqual('updated name', updated['name'])
        self.assertEqual('updated description', updated['description'])
        self.assertFalse(updated['enabled'])

        # Now we update domain by name with name_or_id
        updated = self.operator_cloud.update_domain(
            None,
            name_or_id='updated name',
            name='updated name 2',
            description='updated description 2',
            enabled=True,
        )
        self.assertEqual('updated name 2', updated['name'])
        self.assertEqual('updated description 2', updated['description'])
        self.assertTrue(updated['enabled'])

    def test_delete_domain(self):
        domain = self.operator_cloud.create_domain(
            self.domain_prefix, 'description'
        )
        self.assertEqual(self.domain_prefix, domain['name'])
        self.assertEqual('description', domain['description'])
        self.assertTrue(domain['enabled'])
        deleted = self.operator_cloud.delete_domain(domain['id'])
        self.assertTrue(deleted)

        # Now we delete domain by name with name_or_id
        domain = self.operator_cloud.create_domain(
            self.domain_prefix, 'description'
        )
        self.assertEqual(self.domain_prefix, domain['name'])
        self.assertEqual('description', domain['description'])
        self.assertTrue(domain['enabled'])
        deleted = self.operator_cloud.delete_domain(None, domain['name'])
        self.assertTrue(deleted)

        # Finally, we assert we get False from delete_domain if domain does
        # not exist
        domain = self.operator_cloud.create_domain(
            self.domain_prefix, 'description'
        )
        self.assertEqual(self.domain_prefix, domain['name'])
        self.assertEqual('description', domain['description'])
        self.assertTrue(domain['enabled'])
        deleted = self.operator_cloud.delete_domain(None, 'bogus_domain')
        self.assertFalse(deleted)


class TestEndpoints(base.KeystoneBaseFunctionalTest):
    endpoint_attributes = [
        'id',
        'region',
        'publicurl',
        'internalurl',
        'service_id',
        'adminurl',
    ]

    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        # Generate a random name for services and regions in this test
        self.new_item_name = 'test_' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5)
        )

        self.addCleanup(self._cleanup_services)
        self.addCleanup(self._cleanup_endpoints)

    def _cleanup_endpoints(self):
        exception_list = list()
        for endpoint in self.operator_cloud.list_endpoints():
            if endpoint.get('region') is not None and endpoint[
                'region'
            ].startswith(self.new_item_name):
                try:
                    self.operator_cloud.delete_endpoint(id=endpoint['id'])
                except Exception as exc:
                    # We were unable to delete a service, let's try with next
                    exception_list.append(str(exc))
                    continue
        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise exceptions.SDKException('\n'.join(exception_list))

    def _cleanup_services(self):
        exception_list = list()
        for s in self.operator_cloud.list_services():
            if s['name'] is not None and s['name'].startswith(
                self.new_item_name
            ):
                try:
                    self.operator_cloud.delete_service(name_or_id=s['id'])
                except Exception as e:
                    # We were unable to delete a service, let's try with next
                    exception_list.append(str(e))
                    continue
        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_create_endpoint(self):
        service_name = self.new_item_name + '_create'

        identity = utils.ensure_service_version(
            self.operator_cloud.identity, '3'
        )
        region = next(iter(identity.regions())).id

        service = self.operator_cloud.create_service(
            name=service_name,
            type='test_type',
            description='this is a test description',
        )

        endpoints = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            public_url='http://public.test/',
            internal_url='http://internal.test/',
            admin_url='http://admin.url/',
            region=region,
        )

        self.assertNotEqual([], endpoints)
        self.assertIsNotNone(endpoints[0].get('id'))

        # Test None parameters
        endpoints = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            public_url='http://public.test/',
            region=region,
        )

        self.assertNotEqual([], endpoints)
        self.assertIsNotNone(endpoints[0].get('id'))

    def test_update_endpoint(self):
        # service operations require existing region. Do not test updating
        # region for now
        identity = utils.ensure_service_version(
            self.operator_cloud.identity, '3'
        )
        region = next(iter(identity.regions())).id

        service = self.operator_cloud.create_service(
            name='service1', type='test_type'
        )
        endpoint = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            url='http://admin.url/',
            interface='admin',
            region=region,
            enabled=False,
        )[0]

        new_service = self.operator_cloud.create_service(
            name='service2', type='test_type'
        )
        new_endpoint = self.operator_cloud.update_endpoint(
            endpoint.id,
            service_name_or_id=new_service.id,
            url='http://public.url/',
            interface='public',
            region=region,
            enabled=True,
        )

        self.assertEqual(new_endpoint.url, 'http://public.url/')
        self.assertEqual(new_endpoint.interface, 'public')
        self.assertEqual(new_endpoint.region_id, region)
        self.assertEqual(new_endpoint.service_id, new_service.id)
        self.assertTrue(new_endpoint.is_enabled)

    def test_list_endpoints(self):
        service_name = self.new_item_name + '_list'

        identity = utils.ensure_service_version(
            self.operator_cloud.identity, '3'
        )
        region = next(iter(identity.regions())).id

        service = self.operator_cloud.create_service(
            name=service_name,
            type='test_type',
            description='this is a test description',
        )

        endpoints = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            public_url='http://public.test/',
            internal_url='http://internal.test/',
            region=region,
        )

        observed_endpoints = self.operator_cloud.list_endpoints()
        found = False
        for e in observed_endpoints:
            # Test all attributes are returned
            for endpoint in endpoints:
                if e['id'] == endpoint['id']:
                    found = True
                    self.assertEqual(service['id'], e['service_id'])
                    if 'interface' in e:
                        if e['interface'] == 'internal':
                            self.assertEqual('http://internal.test/', e['url'])
                        elif e['interface'] == 'public':
                            self.assertEqual('http://public.test/', e['url'])
                    else:
                        self.assertEqual('http://public.test/', e['publicurl'])
                        self.assertEqual(
                            'http://internal.test/', e['internalurl']
                        )
                    self.assertEqual(region, e['region_id'])

        self.assertTrue(found, msg='new endpoint not found in endpoints list!')

    def test_delete_endpoint(self):
        service_name = self.new_item_name + '_delete'

        identity = utils.ensure_service_version(
            self.operator_cloud.identity, '3'
        )
        region = next(iter(identity.regions())).id

        service = self.operator_cloud.create_service(
            name=service_name,
            type='test_type',
            description='this is a test description',
        )

        endpoints = self.operator_cloud.create_endpoint(
            service_name_or_id=service['id'],
            public_url='http://public.test/',
            internal_url='http://internal.test/',
            region=region,
        )

        self.assertNotEqual([], endpoints)
        for endpoint in endpoints:
            self.operator_cloud.delete_endpoint(endpoint['id'])

        observed_endpoints = self.operator_cloud.list_endpoints()
        found = False
        for e in observed_endpoints:
            for endpoint in endpoints:
                if e['id'] == endpoint['id']:
                    found = True
                    break
        self.assertEqual(False, found, message='new endpoint was not deleted!')


class TestGroup(base.KeystoneBaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        self.group_prefix = self.getUniqueString('group')
        self.addCleanup(self._cleanup_groups)

    def _cleanup_groups(self):
        exception_list = list()
        for group in self.operator_cloud.list_groups():
            if group['name'].startswith(self.group_prefix):
                try:
                    self.operator_cloud.delete_group(group['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_create_group(self):
        group_name = self.group_prefix + '_create'
        group = self.operator_cloud.create_group(group_name, 'test group')

        for key in ('id', 'name', 'description', 'domain_id'):
            self.assertIn(key, group)
        self.assertEqual(group_name, group['name'])
        self.assertEqual('test group', group['description'])

    def test_delete_group(self):
        group_name = self.group_prefix + '_delete'

        group = self.operator_cloud.create_group(group_name, 'test group')
        self.assertIsNotNone(group)

        self.assertTrue(self.operator_cloud.delete_group(group_name))

        results = self.operator_cloud.search_groups(
            filters=dict(name=group_name)
        )
        self.assertEqual(0, len(results))

    def test_delete_group_not_exists(self):
        self.assertFalse(self.operator_cloud.delete_group('xInvalidGroupx'))

    def test_search_groups(self):
        group_name = self.group_prefix + '_search'

        # Shouldn't find any group with this name yet
        results = self.operator_cloud.search_groups(
            filters=dict(name=group_name)
        )
        self.assertEqual(0, len(results))

        # Now create a new group
        group = self.operator_cloud.create_group(group_name, 'test group')
        self.assertEqual(group_name, group['name'])

        # Now we should find only the new group
        results = self.operator_cloud.search_groups(
            filters=dict(name=group_name)
        )
        self.assertEqual(1, len(results))
        self.assertEqual(group_name, results[0]['name'])

    def test_update_group(self):
        group_name = self.group_prefix + '_update'
        group_desc = 'test group'

        group = self.operator_cloud.create_group(group_name, group_desc)
        self.assertEqual(group_name, group['name'])
        self.assertEqual(group_desc, group['description'])

        updated_group_name = group_name + '_xyz'
        updated_group_desc = group_desc + ' updated'
        updated_group = self.operator_cloud.update_group(
            group_name, name=updated_group_name, description=updated_group_desc
        )
        self.assertEqual(updated_group_name, updated_group['name'])
        self.assertEqual(updated_group_desc, updated_group['description'])


class TestProject(base.KeystoneBaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        self.new_project_name = self.getUniqueString('project')
        self.addCleanup(self._cleanup_projects)

    def _cleanup_projects(self):
        exception_list = list()
        for p in self.operator_cloud.list_projects():
            if p['name'].startswith(self.new_project_name):
                try:
                    self.operator_cloud.delete_project(p['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue
        if exception_list:
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_create_project(self):
        project_name = self.new_project_name + '_create'

        default_domain = self.operator_cloud.get_domain('default')
        assert default_domain is not None
        params = {
            'name': project_name,
            'description': 'test_create_project',
            'domain_id': default_domain['id'],
        }

        project = self.operator_cloud.create_project(**params)

        self.assertIsNotNone(project)
        self.assertEqual(project_name, project['name'])
        self.assertEqual('test_create_project', project['description'])

        user_id = self.operator_cloud.current_user_id

        # Grant the current user access to the project
        self.assertTrue(
            self.operator_cloud.grant_role(
                'member', user=user_id, project=project['id'], wait=True
            )
        )
        self.addCleanup(
            self.operator_cloud.revoke_role,
            'member',
            user=user_id,
            project=project['id'],
            wait=True,
        )

        new_cloud = self.operator_cloud.connect_as_project(project)
        self.add_info_on_exception(
            'new_cloud_config', pprint.pformat(new_cloud.config.config)
        )
        location = new_cloud.current_location
        self.assertEqual(project_name, location['project']['name'])

    def test_update_project(self):
        project_name = self.new_project_name + '_update'

        default_domain = self.operator_cloud.get_domain('default')
        assert default_domain is not None
        params = {
            'name': project_name,
            'description': 'test_update_project',
            'enabled': True,
            'domain_id': default_domain['id'],
        }

        project = self.operator_cloud.create_project(**params)
        updated_project = self.operator_cloud.update_project(
            project_name, enabled=False, description='new'
        )
        self.assertIsNotNone(updated_project)
        self.assertEqual(project['id'], updated_project['id'])
        self.assertEqual(project['name'], updated_project['name'])
        self.assertEqual(updated_project['description'], 'new')
        self.assertTrue(project['enabled'])
        self.assertFalse(updated_project['enabled'])

        # Revert the description and verify the project is still disabled
        updated_project = self.operator_cloud.update_project(
            project_name, description=params['description']
        )
        self.assertIsNotNone(updated_project)
        self.assertEqual(project['id'], updated_project['id'])
        self.assertEqual(project['name'], updated_project['name'])
        self.assertEqual(
            project['description'], updated_project['description']
        )
        self.assertTrue(project['enabled'])
        self.assertFalse(updated_project['enabled'])

    def test_delete_project(self):
        project_name = self.new_project_name + '_delete'
        default_domain = self.operator_cloud.get_domain('default')
        assert default_domain is not None
        params = {
            'name': project_name,
            'domain_id': default_domain['id'],
        }
        project = self.operator_cloud.create_project(**params)
        self.assertIsNotNone(project)
        self.assertTrue(self.operator_cloud.delete_project(project['id']))

    def test_delete_project_not_found(self):
        self.assertFalse(self.operator_cloud.delete_project('doesNotExist'))


class TestRoles(base.KeystoneBaseFunctionalTest):
    def setUp(self):
        super().setUp()

        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        self.role_prefix = 'test_role' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5)
        )
        self.user_prefix = self.getUniqueString('user')
        self.group_prefix = self.getUniqueString('group')

        self.addCleanup(self._cleanup_users)
        self.addCleanup(self._cleanup_groups)
        self.addCleanup(self._cleanup_roles)

    def _cleanup_groups(self):
        exception_list = list()
        for group in self.operator_cloud.list_groups():
            if group['name'].startswith(self.group_prefix):
                try:
                    self.operator_cloud.delete_group(group['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise exceptions.SDKException('\n'.join(exception_list))

    def _cleanup_users(self):
        exception_list = list()
        for user in self.operator_cloud.list_users():
            if user['name'].startswith(self.user_prefix):
                try:
                    self.operator_cloud.delete_user(user['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise exceptions.SDKException('\n'.join(exception_list))

    def _cleanup_roles(self):
        exception_list = list()
        for role in self.operator_cloud.list_roles():
            if role['name'].startswith(self.role_prefix):
                try:
                    self.operator_cloud.delete_role(role['name'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise exceptions.SDKException('\n'.join(exception_list))

    def _create_user(self, **kwargs):
        domain = self.operator_cloud.get_domain('default')
        assert domain is not None
        return self.operator_cloud.create_user(
            domain_id=domain['id'], **kwargs
        )

    def test_list_roles(self):
        roles = self.operator_cloud.list_roles()
        self.assertIsNotNone(roles)
        self.assertNotEqual([], roles)

    def test_get_role(self):
        role = self.operator_cloud.get_role('admin')
        self.assertIsNotNone(role)
        assert role is not None
        self.assertIn('id', role)
        self.assertIn('name', role)
        self.assertEqual('admin', role['name'])

    def test_search_roles(self):
        roles = self.operator_cloud.search_roles(filters={'name': 'admin'})
        self.assertIsNotNone(roles)
        self.assertEqual(1, len(roles))
        self.assertEqual('admin', roles[0]['name'])

    def test_create_role(self):
        role_name = self.role_prefix + '_create_role'
        role = self.operator_cloud.create_role(role_name)
        self.assertIsNotNone(role)
        self.assertIn('id', role)
        self.assertIn('name', role)
        self.assertEqual(role_name, role['name'])

    def test_delete_role(self):
        role_name = self.role_prefix + '_delete_role'
        role = self.operator_cloud.create_role(role_name)
        self.assertIsNotNone(role)
        self.assertTrue(self.operator_cloud.delete_role(role_name))

    # TODO(Shrews): Once we can support assigning roles within shade, we
    # need to make this test a little more specific, and add more for testing
    # filtering functionality.
    def test_list_role_assignments(self):
        assignments = self.operator_cloud.list_role_assignments()
        self.assertIsInstance(assignments, list)
        self.assertGreater(len(assignments), 0)

    def test_list_role_assignments_v2(self):
        user = self.operator_cloud.get_user('demo')
        assert user is not None
        project = self.operator_cloud.get_project('demo')
        assert project is not None
        assignments = self.operator_cloud.list_role_assignments(
            filters={'user': user['id'], 'project': project['id']}
        )
        self.assertIsInstance(assignments, list)
        self.assertGreater(len(assignments), 0)

    def test_grant_revoke_role_user_project(self):
        user_name = self.user_prefix + '_user_project'
        user_email = 'nobody@nowhere.com'
        role_name = self.role_prefix + '_grant_user_project'
        role = self.operator_cloud.create_role(role_name)
        user = self._create_user(
            name=user_name, email=user_email, default_project='demo'
        )
        demo_project = self.operator_cloud.get_project('demo')
        assert demo_project is not None
        self.assertTrue(
            self.operator_cloud.grant_role(
                role_name, user=user['id'], project='demo', wait=True
            )
        )
        assignments = self.operator_cloud.list_role_assignments(
            {
                'role': role['id'],
                'user': user['id'],
                'project': demo_project['id'],
            }
        )
        self.assertIsInstance(assignments, list)
        self.assertEqual(1, len(assignments))
        self.assertTrue(
            self.operator_cloud.revoke_role(
                role_name, user=user['id'], project='demo', wait=True
            )
        )
        assignments = self.operator_cloud.list_role_assignments(
            {
                'role': role['id'],
                'user': user['id'],
                'project': demo_project['id'],
            }
        )
        self.assertIsInstance(assignments, list)
        self.assertEqual(0, len(assignments))

    def test_grant_revoke_role_group_project(self):
        role_name = self.role_prefix + '_grant_group_project'
        role = self.operator_cloud.create_role(role_name)
        group_name = self.group_prefix + '_group_project'
        group = self.operator_cloud.create_group(
            name=group_name, description='test group', domain='default'
        )
        demo_project = self.operator_cloud.get_project('demo')
        assert demo_project is not None
        self.assertTrue(
            self.operator_cloud.grant_role(
                role_name, group=group['id'], project='demo'
            )
        )
        assignments = self.operator_cloud.list_role_assignments(
            {
                'role': role['id'],
                'group': group['id'],
                'project': demo_project['id'],
            }
        )
        self.assertIsInstance(assignments, list)
        self.assertEqual(1, len(assignments))
        self.assertTrue(
            self.operator_cloud.revoke_role(
                role_name, group=group['id'], project='demo'
            )
        )
        assignments = self.operator_cloud.list_role_assignments(
            {
                'role': role['id'],
                'group': group['id'],
                'project': demo_project['id'],
            }
        )
        self.assertIsInstance(assignments, list)
        self.assertEqual(0, len(assignments))

    def test_grant_revoke_role_user_domain(self):
        role_name = self.role_prefix + '_grant_user_domain'
        role = self.operator_cloud.create_role(role_name)
        user_name = self.user_prefix + '_user_domain'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(
            name=user_name, email=user_email, default_project='demo'
        )
        default_domain = self.operator_cloud.get_domain('default')
        assert default_domain is not None
        self.assertTrue(
            self.operator_cloud.grant_role(
                role_name, user=user['id'], domain='default'
            )
        )
        assignments = self.operator_cloud.list_role_assignments(
            {
                'role': role['id'],
                'user': user['id'],
                'domain': default_domain['id'],
            }
        )
        self.assertIsInstance(assignments, list)
        self.assertEqual(1, len(assignments))
        self.assertTrue(
            self.operator_cloud.revoke_role(
                role_name, user=user['id'], domain='default'
            )
        )
        assignments = self.operator_cloud.list_role_assignments(
            {
                'role': role['id'],
                'user': user['id'],
                'domain': default_domain['id'],
            }
        )
        self.assertIsInstance(assignments, list)
        self.assertEqual(0, len(assignments))

    def test_grant_revoke_role_group_domain(self):
        role_name = self.role_prefix + '_grant_group_domain'
        role = self.operator_cloud.create_role(role_name)
        group_name = self.group_prefix + '_group_domain'
        group = self.operator_cloud.create_group(
            name=group_name, description='test group', domain='default'
        )
        default_domain = self.operator_cloud.get_domain('default')
        assert default_domain is not None
        self.assertTrue(
            self.operator_cloud.grant_role(
                role_name, group=group['id'], domain='default'
            )
        )
        assignments = self.operator_cloud.list_role_assignments(
            {
                'role': role['id'],
                'group': group['id'],
                'domain': default_domain['id'],
            }
        )
        self.assertIsInstance(assignments, list)
        self.assertEqual(1, len(assignments))
        self.assertTrue(
            self.operator_cloud.revoke_role(
                role_name, group=group['id'], domain='default'
            )
        )
        assignments = self.operator_cloud.list_role_assignments(
            {
                'role': role['id'],
                'group': group['id'],
                'domain': default_domain['id'],
            }
        )
        self.assertIsInstance(assignments, list)
        self.assertEqual(0, len(assignments))

    def test_grant_revoke_role_user_system(self):
        role_name = self.role_prefix + '_grant_user_system'
        role = self.operator_cloud.create_role(role_name)
        user_name = self.user_prefix + '_user_system'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(
            name=user_name, email=user_email, default_project='demo'
        )
        self.assertTrue(
            self.operator_cloud.grant_role(
                role_name, user=user['id'], system='all'
            )
        )
        assignments = self.operator_cloud.list_role_assignments(
            {'role': role['id'], 'user': user['id'], 'system': 'all'}
        )
        self.assertIsInstance(assignments, list)
        self.assertEqual(1, len(assignments))
        self.assertTrue(
            self.operator_cloud.revoke_role(
                role_name, user=user['id'], system='all'
            )
        )
        assignments = self.operator_cloud.list_role_assignments(
            {'role': role['id'], 'user': user['id'], 'system': 'all'}
        )
        self.assertIsInstance(assignments, list)
        self.assertEqual(0, len(assignments))

    def test_grant_revoke_role_group_system(self):
        role_name = self.role_prefix + '_grant_group_system'
        role = self.operator_cloud.create_role(role_name)
        group_name = self.group_prefix + '_group_system'
        group = self.operator_cloud.create_group(
            name=group_name, description='test group'
        )
        self.assertTrue(
            self.operator_cloud.grant_role(
                role_name, group=group['id'], system='all'
            )
        )
        assignments = self.operator_cloud.list_role_assignments(
            {'role': role['id'], 'group': group['id'], 'system': 'all'}
        )
        self.assertIsInstance(assignments, list)
        self.assertEqual(1, len(assignments))
        self.assertTrue(
            self.operator_cloud.revoke_role(
                role_name, group=group['id'], system='all'
            )
        )
        assignments = self.operator_cloud.list_role_assignments(
            {'role': role['id'], 'group': group['id'], 'system': 'all'}
        )
        self.assertIsInstance(assignments, list)
        self.assertEqual(0, len(assignments))


class TestServices(base.KeystoneBaseFunctionalTest):
    service_attributes = ['id', 'name', 'type', 'description']

    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        # Generate a random name for services in this test
        self.new_service_name = 'test_' + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(5)
        )

        self.addCleanup(self._cleanup_services)

    def _cleanup_services(self):
        exception_list = list()
        for s in self.operator_cloud.list_services():
            if s['name'] is not None and s['name'].startswith(
                self.new_service_name
            ):
                try:
                    self.operator_cloud.delete_service(name_or_id=s['id'])
                except Exception as e:
                    # We were unable to delete a service, let's try with next
                    exception_list.append(str(e))
                    continue
        if exception_list:
            # Raise an error: we must make users aware that something went
            # wrong
            raise exceptions.SDKException('\n'.join(exception_list))

    def test_create_service(self):
        service = self.operator_cloud.create_service(
            name=self.new_service_name + '_create',
            type='test_type',
            description='this is a test description',
        )
        self.assertIsNotNone(service.get('id'))

    def test_update_service(self):
        service = self.operator_cloud.create_service(
            name=self.new_service_name + '_create',
            type='test_type',
            description='this is a test description',
            enabled=True,
        )
        new_service = self.operator_cloud.update_service(
            service.id,
            name=self.new_service_name + '_update',
            description='this is an updated description',
            enabled=False,
        )
        self.assertEqual(new_service.name, self.new_service_name + '_update')
        self.assertEqual(
            new_service.description, 'this is an updated description'
        )
        self.assertFalse(new_service.is_enabled)
        self.assertEqual(service.id, new_service.id)

    def test_list_services(self):
        service = self.operator_cloud.create_service(
            name=self.new_service_name + '_list', type='test_type'
        )
        observed_services = self.operator_cloud.list_services()
        self.assertIsInstance(observed_services, list)
        found = False
        for s in observed_services:
            # Test all attributes are returned
            if s['id'] == service['id']:
                self.assertEqual(
                    self.new_service_name + '_list', s.get('name')
                )
                self.assertEqual('test_type', s.get('type'))
                found = True
        self.assertTrue(found, msg='new service not found in service list!')

    def test_delete_service_by_name(self):
        # Test delete by name
        service = self.operator_cloud.create_service(
            name=self.new_service_name + '_delete_by_name', type='test_type'
        )
        self.operator_cloud.delete_service(name_or_id=service['name'])
        observed_services = self.operator_cloud.list_services()
        found = False
        for s in observed_services:
            if s['id'] == service['id']:
                found = True
                break
        self.assertEqual(False, found, message='service was not deleted!')

    def test_delete_service_by_id(self):
        # Test delete by id
        service = self.operator_cloud.create_service(
            name=self.new_service_name + '_delete_by_id', type='test_type'
        )
        self.operator_cloud.delete_service(name_or_id=service['id'])
        observed_services = self.operator_cloud.list_services()
        found = False
        for s in observed_services:
            if s['id'] == service['id']:
                found = True
        self.assertEqual(False, found, message='service was not deleted!')


class TestUsers(base.KeystoneBaseFunctionalTest):
    def setUp(self):
        super().setUp()
        if not self.operator_cloud:
            self.skipTest("Operator cloud is required for this test")

        self.user_prefix = self.getUniqueString('user')
        self.addCleanup(self._cleanup_users)

    def _cleanup_users(self):
        exception_list = list()
        for user in self.operator_cloud.list_users():
            if user['name'].startswith(self.user_prefix):
                try:
                    self.operator_cloud.delete_user(user['id'])
                except Exception as e:
                    exception_list.append(str(e))
                    continue

        if exception_list:
            raise exceptions.SDKException('\n'.join(exception_list))

    def _create_user(self, **kwargs):
        domain = self.operator_cloud.get_domain('default')
        assert domain is not None
        return self.operator_cloud.create_user(
            domain_id=domain['id'], **kwargs
        )

    def test_list_users(self):
        users = self.operator_cloud.list_users()
        self.assertIsNotNone(users)
        self.assertNotEqual([], users)

    def test_get_user(self):
        user = self.operator_cloud.get_user('admin')
        self.assertIsNotNone(user)
        assert user is not None
        self.assertIn('id', user)
        self.assertIn('name', user)
        self.assertEqual('admin', user['name'])

    def test_search_users(self):
        users = self.operator_cloud.search_users(filters={'is_enabled': True})
        self.assertIsNotNone(users)

    def test_search_users_jmespath(self):
        users = self.operator_cloud.search_users(filters="[?enabled]")
        self.assertIsNotNone(users)

    def test_create_user(self):
        user_name = self.user_prefix + '_create'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(name=user_name, email=user_email)
        self.assertIsNotNone(user)
        self.assertEqual(user_name, user['name'])
        self.assertEqual(user_email, user['email'])
        self.assertTrue(user['is_enabled'])

    def test_delete_user(self):
        user_name = self.user_prefix + '_delete'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(name=user_name, email=user_email)
        self.assertIsNotNone(user)
        self.assertTrue(self.operator_cloud.delete_user(user['id']))

    def test_delete_user_not_found(self):
        self.assertFalse(self.operator_cloud.delete_user('does_not_exist'))

    def test_update_user(self):
        user_name = self.user_prefix + '_updatev3'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(name=user_name, email=user_email)
        self.assertIsNotNone(user)
        self.assertTrue(user['is_enabled'])

        # Pass some keystone v3 params. This should work no matter which
        # version of keystone we are testing against.
        new_user = self.operator_cloud.update_user(
            user['id'],
            name=user_name + '2',
            email='somebody@nowhere.com',
            enabled=False,
            password='secret',
            description='',
        )
        self.assertIsNotNone(new_user)
        self.assertEqual(user['id'], new_user['id'])
        self.assertEqual(user_name + '2', new_user['name'])
        self.assertEqual('somebody@nowhere.com', new_user['email'])
        self.assertFalse(new_user['is_enabled'])

    def test_update_user_password(self):
        user_name = self.user_prefix + '_password'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(
            name=user_name, email=user_email, password='old_secret'
        )
        self.assertIsNotNone(user)
        self.assertTrue(user['enabled'])

        # This should work for both v2 and v3
        new_user = self.operator_cloud.update_user(
            user['id'], password='new_secret'
        )
        self.assertIsNotNone(new_user)
        self.assertEqual(user['id'], new_user['id'])
        self.assertEqual(user_name, new_user['name'])
        self.assertEqual(user_email, new_user['email'])
        self.assertTrue(new_user['enabled'])
        self.assertTrue(
            self.operator_cloud.grant_role(
                'member', user=user['id'], project='demo', wait=True
            )
        )
        self.addCleanup(
            self.operator_cloud.revoke_role,
            'member',
            user=user['id'],
            project='demo',
            wait=True,
        )

        new_cloud = self.operator_cloud.connect_as(
            user_id=user['id'], password='new_secret', project_name='demo'
        )

        self.assertIsNotNone(new_cloud)
        location = new_cloud.current_location
        self.assertEqual(location['project']['name'], 'demo')
        self.assertIsNotNone(new_cloud.service_catalog)

    def test_users_and_groups(self):
        group_name = self.getUniqueString('group')
        self.addCleanup(self.operator_cloud.delete_group, group_name)

        # Create a group
        group = self.operator_cloud.create_group(group_name, 'test group')
        self.assertIsNotNone(group)

        # Create a user
        user_name = self.user_prefix + '_ug'
        user_email = 'nobody@nowhere.com'
        user = self._create_user(name=user_name, email=user_email)
        self.assertIsNotNone(user)

        # Add the user to the group
        self.operator_cloud.add_user_to_group(user_name, group_name)
        self.assertTrue(
            self.operator_cloud.is_user_in_group(user_name, group_name)
        )

        # Remove them from the group
        self.operator_cloud.remove_user_from_group(user_name, group_name)
        self.assertFalse(
            self.operator_cloud.is_user_in_group(user_name, group_name)
        )
