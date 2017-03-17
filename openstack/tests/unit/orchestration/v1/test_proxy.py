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

import mock
import six

from openstack import exceptions
from openstack.orchestration.v1 import _proxy
from openstack.orchestration.v1 import resource
from openstack.orchestration.v1 import software_config as sc
from openstack.orchestration.v1 import software_deployment as sd
from openstack.orchestration.v1 import stack
from openstack.orchestration.v1 import stack_environment
from openstack.orchestration.v1 import stack_files
from openstack.orchestration.v1 import stack_template
from openstack.orchestration.v1 import template
from openstack.tests.unit import test_proxy_base2


class TestOrchestrationProxy(test_proxy_base2.TestProxyBase):
    def setUp(self):
        super(TestOrchestrationProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)

    def test_create_stack(self):
        self.verify_create(self.proxy.create_stack, stack.Stack)

    def test_create_stack_preview(self):
        method_kwargs = {"preview": True, "x": 1, "y": 2, "z": 3}
        self.verify_create(self.proxy.create_stack, stack.StackPreview,
                           method_kwargs=method_kwargs)

    def test_find_stack(self):
        self.verify_find(self.proxy.find_stack, stack.Stack)

    def test_stacks(self):
        self.verify_list(self.proxy.stacks, stack.Stack, paginated=False)

    def test_get_stack(self):
        self.verify_get(self.proxy.get_stack, stack.Stack)

    def test_update_stack(self):
        self.verify_update(self.proxy.update_stack, stack.Stack)

    def test_delete_stack(self):
        self.verify_delete(self.proxy.delete_stack, stack.Stack, False)

    def test_delete_stack_ignore(self):
        self.verify_delete(self.proxy.delete_stack, stack.Stack, True)

    @mock.patch.object(stack.Stack, 'check')
    def test_check_stack_with_stack_object(self, mock_check):
        stk = stack.Stack(id='FAKE_ID')

        res = self.proxy.check_stack(stk)

        self.assertIsNone(res)
        mock_check.assert_called_once_with(self.proxy._session)

    @mock.patch.object(stack.Stack, 'existing')
    def test_check_stack_with_stack_ID(self, mock_stack):
        stk = mock.Mock()
        mock_stack.return_value = stk

        res = self.proxy.check_stack('FAKE_ID')

        self.assertIsNone(res)
        mock_stack.assert_called_once_with(id='FAKE_ID')
        stk.check.assert_called_once_with(self.proxy._session)

    @mock.patch.object(stack.Stack, 'find')
    def test_get_stack_environment_with_stack_identity(self, mock_find):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)
        mock_find.return_value = stk

        self._verify2('openstack.proxy2.BaseProxy._get',
                      self.proxy.get_stack_environment,
                      method_args=['IDENTITY'],
                      expected_args=[stack_environment.StackEnvironment],
                      expected_kwargs={'requires_id': False,
                                       'stack_name': stack_name,
                                       'stack_id': stack_id})
        mock_find.assert_called_once_with(mock.ANY, 'IDENTITY',
                                          ignore_missing=False)

    def test_get_stack_environment_with_stack_object(self):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)

        self._verify2('openstack.proxy2.BaseProxy._get',
                      self.proxy.get_stack_environment,
                      method_args=[stk],
                      expected_args=[stack_environment.StackEnvironment],
                      expected_kwargs={'requires_id': False,
                                       'stack_name': stack_name,
                                       'stack_id': stack_id})

    @mock.patch.object(stack_files.StackFiles, 'get')
    @mock.patch.object(stack.Stack, 'find')
    def test_get_stack_files_with_stack_identity(self, mock_find, mock_get):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)
        mock_find.return_value = stk
        mock_get.return_value = {'file': 'content'}

        res = self.proxy.get_stack_files('IDENTITY')

        self.assertEqual({'file': 'content'}, res)
        mock_find.assert_called_once_with(mock.ANY, 'IDENTITY',
                                          ignore_missing=False)
        mock_get.assert_called_once_with(self.proxy._session)

    @mock.patch.object(stack_files.StackFiles, 'get')
    def test_get_stack_files_with_stack_object(self, mock_get):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)
        mock_get.return_value = {'file': 'content'}

        res = self.proxy.get_stack_files(stk)

        self.assertEqual({'file': 'content'}, res)
        mock_get.assert_called_once_with(self.proxy._session)

    @mock.patch.object(stack.Stack, 'find')
    def test_get_stack_template_with_stack_identity(self, mock_find):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)
        mock_find.return_value = stk

        self._verify2('openstack.proxy2.BaseProxy._get',
                      self.proxy.get_stack_template,
                      method_args=['IDENTITY'],
                      expected_args=[stack_template.StackTemplate],
                      expected_kwargs={'requires_id': False,
                                       'stack_name': stack_name,
                                       'stack_id': stack_id})
        mock_find.assert_called_once_with(mock.ANY, 'IDENTITY',
                                          ignore_missing=False)

    def test_get_stack_template_with_stack_object(self):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)

        self._verify2('openstack.proxy2.BaseProxy._get',
                      self.proxy.get_stack_template,
                      method_args=[stk],
                      expected_args=[stack_template.StackTemplate],
                      expected_kwargs={'requires_id': False,
                                       'stack_name': stack_name,
                                       'stack_id': stack_id})

    @mock.patch.object(stack.Stack, 'find')
    def test_resources_with_stack_object(self, mock_find):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)

        self.verify_list(self.proxy.resources, resource.Resource,
                         paginated=False, method_args=[stk],
                         expected_kwargs={'stack_name': stack_name,
                                          'stack_id': stack_id})

        self.assertEqual(0, mock_find.call_count)

    @mock.patch.object(stack.Stack, 'find')
    def test_resources_with_stack_name(self, mock_find):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)
        mock_find.return_value = stk

        self.verify_list(self.proxy.resources, resource.Resource,
                         paginated=False, method_args=[stack_id],
                         expected_kwargs={'stack_name': stack_name,
                                          'stack_id': stack_id})

        mock_find.assert_called_once_with(mock.ANY, stack_id,
                                          ignore_missing=False)

    @mock.patch.object(stack.Stack, 'find')
    @mock.patch.object(resource.Resource, 'list')
    def test_resources_stack_not_found(self, mock_list, mock_find):
        stack_name = 'test_stack'
        mock_find.side_effect = exceptions.ResourceNotFound(
            'No stack found for test_stack')

        ex = self.assertRaises(exceptions.ResourceNotFound,
                               self.proxy.resources, stack_name)
        self.assertEqual('ResourceNotFound: No stack found for test_stack',
                         six.text_type(ex))

    def test_create_software_config(self):
        self.verify_create(self.proxy.create_software_config,
                           sc.SoftwareConfig)

    def test_software_configs(self):
        self.verify_list(self.proxy.software_configs, sc.SoftwareConfig,
                         paginated=True)

    def test_get_software_config(self):
        self.verify_get(self.proxy.get_software_config, sc.SoftwareConfig)

    def test_delete_software_config(self):
        self.verify_delete(self.proxy.delete_software_config,
                           sc.SoftwareConfig, True)
        self.verify_delete(self.proxy.delete_software_config,
                           sc.SoftwareConfig, False)

    def test_create_software_deployment(self):
        self.verify_create(self.proxy.create_software_deployment,
                           sd.SoftwareDeployment)

    def test_software_deployments(self):
        self.verify_list(self.proxy.software_deployments,
                         sd.SoftwareDeployment, paginated=False)

    def test_get_software_deployment(self):
        self.verify_get(self.proxy.get_software_deployment,
                        sd.SoftwareDeployment)

    def test_update_software_deployment(self):
        self.verify_update(self.proxy.update_software_deployment,
                           sd.SoftwareDeployment)

    def test_delete_software_deployment(self):
        self.verify_delete(self.proxy.delete_software_deployment,
                           sd.SoftwareDeployment, True)
        self.verify_delete(self.proxy.delete_software_deployment,
                           sd.SoftwareDeployment, False)

    @mock.patch.object(template.Template, 'validate')
    def test_validate_template(self, mock_validate):
        tmpl = mock.Mock()
        env = mock.Mock()
        tmpl_url = 'A_URI'
        ignore_errors = 'a_string'

        res = self.proxy.validate_template(tmpl, env, tmpl_url, ignore_errors)

        mock_validate.assert_called_once_with(
            self.proxy._session, tmpl, environment=env, template_url=tmpl_url,
            ignore_errors=ignore_errors)
        self.assertEqual(mock_validate.return_value, res)

    def test_validate_template_invalid_request(self):
        err = self.assertRaises(exceptions.InvalidRequest,
                                self.proxy.validate_template,
                                None, template_url=None)
        self.assertEqual("'template_url' must be specified when template is "
                         "None", six.text_type(err))
