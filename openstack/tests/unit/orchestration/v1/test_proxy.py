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

from testscenarios import load_tests_apply_scenarios as load_tests  # noqa

from openstack import exceptions
from openstack.orchestration.v1 import _proxy
from openstack.orchestration.v1 import resource
from openstack.orchestration.v1 import software_config as sc
from openstack.orchestration.v1 import software_deployment as sd
from openstack.orchestration.v1 import stack
from openstack.orchestration.v1 import stack_environment
from openstack.orchestration.v1 import stack_event
from openstack.orchestration.v1 import stack_files
from openstack.orchestration.v1 import stack_template
from openstack.orchestration.v1 import template
from openstack import proxy
from openstack.tests.unit import test_proxy_base


class TestOrchestrationProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super().setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestOrchestrationStack(TestOrchestrationProxy):
    def test_create_stack(self):
        self.verify_create(self.proxy.create_stack, stack.Stack)

    def test_create_stack_preview(self):
        self.verify_create(
            self.proxy.create_stack,
            stack.Stack,
            method_kwargs={"preview": True, "x": 1, "y": 2, "z": 3},
            expected_kwargs={"x": 1, "y": 2, "z": 3},
        )

    def test_find_stack(self):
        self.verify_find(
            self.proxy.find_stack,
            stack.Stack,
            expected_kwargs={'resolve_outputs': True},
        )
        # mock_method="openstack.proxy.Proxy._find"
        # test_method=self.proxy.find_stack
        # method_kwargs = {
        #     'resolve_outputs': False,
        #     'ignore_missing': False
        # }
        # method_args=["name_or_id"]
        # self._verify(
        #     mock_method, test_method,
        #     method_args=method_args,
        #     method_kwargs=method_kwargs,
        #     expected_args=[stack.Stack, "name_or_id"],
        #     expected_kwargs=method_kwargs,
        #     expected_result="result")
        #
        # method_kwargs = {
        #     'resolve_outputs': True,
        #     'ignore_missing': True
        # }
        # self._verify(
        #     mock_method, test_method,
        #     method_args=method_args,
        #     method_kwargs=method_kwargs,
        #     expected_args=[stack.Stack, "name_or_id"],
        #     expected_kwargs=method_kwargs,
        #     expected_result="result")

    def test_stacks(self):
        self.verify_list(self.proxy.stacks, stack.Stack)

    def test_get_stack(self):
        self.verify_get(
            self.proxy.get_stack,
            stack.Stack,
            method_kwargs={'resolve_outputs': False},
            expected_kwargs={'resolve_outputs': False},
        )
        self.verify_get_overrided(
            self.proxy, stack.Stack, 'openstack.orchestration.v1.stack.Stack'
        )

    def test_update_stack(self):
        self._verify(
            'openstack.orchestration.v1.stack.Stack.commit',
            self.proxy.update_stack,
            expected_result='result',
            method_args=['stack'],
            method_kwargs={'preview': False},
            expected_args=[self.proxy, False],
        )

    def test_update_stack_preview(self):
        self._verify(
            'openstack.orchestration.v1.stack.Stack.commit',
            self.proxy.update_stack,
            expected_result='result',
            method_args=['stack'],
            method_kwargs={'preview': True},
            expected_args=[self.proxy, True],
        )

    def test_abandon_stack(self):
        self._verify(
            'openstack.orchestration.v1.stack.Stack.abandon',
            self.proxy.abandon_stack,
            expected_result='result',
            method_args=['stack'],
            expected_args=[self.proxy],
        )

    @mock.patch.object(stack.Stack, 'find')
    def test_export_stack_with_identity(self, mock_find):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)
        mock_find.return_value = stk

        self._verify(
            'openstack.orchestration.v1.stack.Stack.export',
            self.proxy.export_stack,
            method_args=['IDENTITY'],
            expected_args=[self.proxy],
        )
        mock_find.assert_called_once_with(
            mock.ANY, 'IDENTITY', ignore_missing=False
        )

    def test_export_stack_with_object(self):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)

        self._verify(
            'openstack.orchestration.v1.stack.Stack.export',
            self.proxy.export_stack,
            method_args=[stk],
            expected_args=[self.proxy],
        )

    def test_suspend_stack(self):
        self._verify(
            'openstack.orchestration.v1.stack.Stack.suspend',
            self.proxy.suspend_stack,
            method_args=['stack'],
            expected_args=[self.proxy],
        )

    def test_resume_stack(self):
        self._verify(
            'openstack.orchestration.v1.stack.Stack.resume',
            self.proxy.resume_stack,
            method_args=['stack'],
            expected_args=[self.proxy],
        )

    def test_delete_stack(self):
        self.verify_delete(self.proxy.delete_stack, stack.Stack, False)

    def test_delete_stack_ignore(self):
        self.verify_delete(self.proxy.delete_stack, stack.Stack, True)

    @mock.patch.object(stack.Stack, 'check')
    def test_check_stack_with_stack_object(self, mock_check):
        stk = stack.Stack(id='FAKE_ID')

        res = self.proxy.check_stack(stk)

        self.assertIsNone(res)
        mock_check.assert_called_once_with(self.proxy)

    @mock.patch.object(stack.Stack, 'existing')
    def test_check_stack_with_stack_ID(self, mock_stack):
        stk = mock.Mock()
        mock_stack.return_value = stk

        res = self.proxy.check_stack('FAKE_ID')

        self.assertIsNone(res)
        mock_stack.assert_called_once_with(id='FAKE_ID')
        stk.check.assert_called_once_with(self.proxy)


class TestOrchestrationStackEnvironment(TestOrchestrationProxy):
    @mock.patch.object(stack.Stack, 'find')
    def test_get_stack_environment_with_stack_identity(self, mock_find):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)
        mock_find.return_value = stk

        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_stack_environment,
            method_args=['IDENTITY'],
            expected_args=[stack_environment.StackEnvironment],
            expected_kwargs={
                'requires_id': False,
                'stack_name': stack_name,
                'stack_id': stack_id,
            },
        )
        mock_find.assert_called_once_with(
            mock.ANY, 'IDENTITY', ignore_missing=False
        )

    def test_get_stack_environment_with_stack_object(self):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)

        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_stack_environment,
            method_args=[stk],
            expected_args=[stack_environment.StackEnvironment],
            expected_kwargs={
                'requires_id': False,
                'stack_name': stack_name,
                'stack_id': stack_id,
            },
        )


class TestOrchestrationStackFiles(TestOrchestrationProxy):
    @mock.patch.object(stack_files.StackFiles, 'fetch')
    @mock.patch.object(stack.Stack, 'find')
    def test_get_stack_files_with_stack_identity(self, mock_find, mock_fetch):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)
        mock_find.return_value = stk
        mock_fetch.return_value = {'file': 'content'}

        res = self.proxy.get_stack_files('IDENTITY')

        self.assertEqual({'file': 'content'}, res)
        mock_find.assert_called_once_with(
            mock.ANY, 'IDENTITY', ignore_missing=False
        )
        mock_fetch.assert_called_once_with(self.proxy)

    @mock.patch.object(stack_files.StackFiles, 'fetch')
    def test_get_stack_files_with_stack_object(self, mock_fetch):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)
        mock_fetch.return_value = {'file': 'content'}

        res = self.proxy.get_stack_files(stk)

        self.assertEqual({'file': 'content'}, res)
        mock_fetch.assert_called_once_with(self.proxy)


class TestOrchestrationStackTemplate(TestOrchestrationProxy):
    @mock.patch.object(stack.Stack, 'find')
    def test_get_stack_template_with_stack_identity(self, mock_find):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)
        mock_find.return_value = stk

        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_stack_template,
            method_args=['IDENTITY'],
            expected_args=[stack_template.StackTemplate],
            expected_kwargs={
                'requires_id': False,
                'stack_name': stack_name,
                'stack_id': stack_id,
            },
        )
        mock_find.assert_called_once_with(
            mock.ANY, 'IDENTITY', ignore_missing=False
        )

    def test_get_stack_template_with_stack_object(self):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)

        self._verify(
            'openstack.proxy.Proxy._get',
            self.proxy.get_stack_template,
            method_args=[stk],
            expected_args=[stack_template.StackTemplate],
            expected_kwargs={
                'requires_id': False,
                'stack_name': stack_name,
                'stack_id': stack_id,
            },
        )


class TestOrchestrationResource(TestOrchestrationProxy):
    @mock.patch.object(stack.Stack, 'find')
    def test_resources_with_stack_object(self, mock_find):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)

        self.verify_list(
            self.proxy.resources,
            resource.Resource,
            method_args=[stk],
            expected_args=[],
            expected_kwargs={'stack_name': stack_name, 'stack_id': stack_id},
        )

        self.assertEqual(0, mock_find.call_count)

    @mock.patch.object(stack.Stack, 'find')
    def test_resources_with_stack_name(self, mock_find):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)
        mock_find.return_value = stk

        self.verify_list(
            self.proxy.resources,
            resource.Resource,
            method_args=[stack_id],
            expected_args=[],
            expected_kwargs={'stack_name': stack_name, 'stack_id': stack_id},
        )

        mock_find.assert_called_once_with(
            mock.ANY, stack_id, ignore_missing=False
        )

    @mock.patch.object(stack.Stack, 'find')
    @mock.patch.object(resource.Resource, 'list')
    def test_resources_stack_not_found(self, mock_list, mock_find):
        stack_name = 'test_stack'
        mock_find.side_effect = exceptions.NotFoundException(
            'No stack found for test_stack'
        )

        ex = self.assertRaises(
            exceptions.NotFoundException, self.proxy.resources, stack_name
        )
        self.assertEqual('No stack found for test_stack', str(ex))


class TestOrchestrationSoftwareConfig(TestOrchestrationProxy):
    def test_create_software_config(self):
        self.verify_create(
            self.proxy.create_software_config, sc.SoftwareConfig
        )

    def test_software_configs(self):
        self.verify_list(self.proxy.software_configs, sc.SoftwareConfig)

    def test_get_software_config(self):
        self.verify_get(self.proxy.get_software_config, sc.SoftwareConfig)

    def test_delete_software_config(self):
        self.verify_delete(
            self.proxy.delete_software_config, sc.SoftwareConfig, True
        )
        self.verify_delete(
            self.proxy.delete_software_config, sc.SoftwareConfig, False
        )


class TestOrchestrationSoftwareDeployment(TestOrchestrationProxy):
    def test_create_software_deployment(self):
        self.verify_create(
            self.proxy.create_software_deployment, sd.SoftwareDeployment
        )

    def test_software_deployments(self):
        self.verify_list(
            self.proxy.software_deployments, sd.SoftwareDeployment
        )

    def test_get_software_deployment(self):
        self.verify_get(
            self.proxy.get_software_deployment, sd.SoftwareDeployment
        )

    def test_update_software_deployment(self):
        self.verify_update(
            self.proxy.update_software_deployment, sd.SoftwareDeployment
        )

    def test_delete_software_deployment(self):
        self.verify_delete(
            self.proxy.delete_software_deployment, sd.SoftwareDeployment, True
        )
        self.verify_delete(
            self.proxy.delete_software_deployment, sd.SoftwareDeployment, False
        )


class TestOrchestrationTemplate(TestOrchestrationProxy):
    @mock.patch.object(template.Template, 'validate')
    def test_validate_template(self, mock_validate):
        tmpl = mock.Mock()
        env = mock.Mock()
        tmpl_url = 'A_URI'
        ignore_errors = 'a_string'

        res = self.proxy.validate_template(tmpl, env, tmpl_url, ignore_errors)

        mock_validate.assert_called_once_with(
            self.proxy,
            tmpl,
            environment=env,
            template_url=tmpl_url,
            ignore_errors=ignore_errors,
        )
        self.assertEqual(mock_validate.return_value, res)

    def test_validate_template_no_env(self):
        tmpl = "openstack/tests/unit/orchestration/v1/hello_world.yaml"

        res = self.proxy.read_env_and_templates(tmpl)

        self.assertIsInstance(res, dict)
        self.assertIsInstance(res["files"], dict)

    def test_validate_template_invalid_request(self):
        err = self.assertRaises(
            exceptions.InvalidRequest,
            self.proxy.validate_template,
            None,
            template_url=None,
        )
        self.assertEqual(
            "'template_url' must be specified when template is None",
            str(err),
        )


class TestExtractName(TestOrchestrationProxy):
    scenarios = [
        ('stacks', dict(url='/stacks', parts=['stacks'])),
        ('name_id', dict(url='/stacks/name/id', parts=['stack'])),
        ('identity', dict(url='/stacks/id', parts=['stack'])),
        (
            'preview',
            dict(url='/stacks/name/preview', parts=['stack', 'preview']),
        ),
        (
            'stack_act',
            dict(url='/stacks/name/id/preview', parts=['stack', 'preview']),
        ),
        (
            'stack_subres',
            dict(
                url='/stacks/name/id/resources', parts=['stack', 'resources']
            ),
        ),
        (
            'stack_subres_id',
            dict(
                url='/stacks/name/id/resources/id', parts=['stack', 'resource']
            ),
        ),
        (
            'stack_subres_id_act',
            dict(
                url='/stacks/name/id/resources/id/action',
                parts=['stack', 'resource', 'action'],
            ),
        ),
        (
            'event',
            dict(
                url='/stacks/ignore/ignore/resources/ignore/events/id',
                parts=['stack', 'resource', 'event'],
            ),
        ),
        (
            'sd_metadata',
            dict(
                url='/software_deployments/metadata/ignore',
                parts=['software_deployment', 'metadata'],
            ),
        ),
    ]

    def test_extract_name(self):
        results = self.proxy._extract_name(self.url)
        self.assertEqual(self.parts, results)


class TestOrchestrationStackEvents(TestOrchestrationProxy):
    def test_stack_events_with_stack_object(self):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)

        self._verify(
            'openstack.proxy.Proxy._list',
            self.proxy.stack_events,
            method_args=[stk],
            expected_args=[stack_event.StackEvent],
            expected_kwargs={
                'stack_name': stack_name,
                'stack_id': stack_id,
            },
        )

    @mock.patch.object(proxy.Proxy, '_get')
    def test_stack_events_with_stack_id(self, mock_get):
        stack_id = '1234'
        stack_name = 'test_stack'
        stk = stack.Stack(id=stack_id, name=stack_name)
        mock_get.return_value = stk

        self._verify(
            'openstack.proxy.Proxy._list',
            self.proxy.stack_events,
            method_args=[stk],
            expected_args=[stack_event.StackEvent],
            expected_kwargs={
                'stack_name': stack_name,
                'stack_id': stack_id,
            },
        )

    def test_stack_events_with_resource_name(self):
        stack_id = '1234'
        stack_name = 'test_stack'
        resource_name = 'id'
        base_path = '/stacks/%(stack_name)s/%(stack_id)s/resources/%(resource_name)s/events'
        stk = stack.Stack(id=stack_id, name=stack_name)

        self._verify(
            'openstack.proxy.Proxy._list',
            self.proxy.stack_events,
            method_args=[stk, resource_name],
            expected_args=[stack_event.StackEvent],
            expected_kwargs={
                'stack_name': stack_name,
                'stack_id': stack_id,
                'resource_name': resource_name,
                'base_path': base_path,
            },
        )
