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

from openstack.tests.unit import base


class TestProxyBase(base.TestCase):
    def setUp(self):
        super().setUp()
        self.session = mock.Mock()

    def _verify(
        self,
        mock_method,
        test_method,
        *,
        method_args=None,
        method_kwargs=None,
        method_result=None,
        expected_args=None,
        expected_kwargs=None,
        expected_result=None,
    ):
        with mock.patch(mock_method) as mocked:
            mocked.return_value = expected_result
            if any(
                [
                    method_args,
                    method_kwargs,
                    expected_args,
                    expected_kwargs,
                ]
            ):
                method_args = method_args or ()
                method_kwargs = method_kwargs or {}
                expected_args = expected_args or ()
                expected_kwargs = expected_kwargs or {}

                if method_result:
                    self.assertEqual(
                        method_result,
                        test_method(*method_args, **method_kwargs),
                    )
                else:
                    self.assertEqual(
                        expected_result,
                        test_method(*method_args, **method_kwargs),
                    )

                # Check how the mock was called in detail
                called_args, called_kwargs = mocked.call_args
                self.assertEqual(expected_args, list(called_args))

                # NOTE(gtema): if base_path is not in expected_kwargs or empty
                # exclude it from the comparison, since some methods might
                # still invoke method with None value
                base_path = expected_kwargs.get('base_path', None)
                if base_path is None:
                    expected_kwargs.pop('base_path', None)
                    called_kwargs.pop('base_path', None)
                # ditto for paginated
                paginated = expected_kwargs.get('paginated', None)
                if paginated is None:
                    expected_kwargs.pop('paginated', None)
                    called_kwargs.pop('paginated', None)
                # and ignore_missing
                ignore_missing = expected_kwargs.get('ignore_missing', None)
                if ignore_missing is None:
                    expected_kwargs.pop('ignore_missing', None)
                    called_kwargs.pop('ignore_missing', None)

                self.assertDictEqual(expected_kwargs, called_kwargs)
            else:
                self.assertEqual(expected_result, test_method())
                mocked.assert_called_with(test_method.__self__)

    def verify_create(
        self,
        test_method,
        resource_type,
        base_path=None,
        *,
        method_args=None,
        method_kwargs=None,
        expected_args=None,
        expected_kwargs=None,
        expected_result="result",
        mock_method="openstack.proxy.Proxy._create",
    ):
        if method_args is None:
            method_args = []
        if method_kwargs is None:
            method_kwargs = {"x": 1, "y": 2, "z": 3}
        if expected_args is None:
            expected_args = method_args.copy()
        if expected_kwargs is None:
            expected_kwargs = method_kwargs.copy()
        expected_kwargs["base_path"] = base_path

        self._verify(
            mock_method,
            test_method,
            method_args=method_args,
            method_kwargs=method_kwargs,
            expected_args=[resource_type] + expected_args,
            expected_kwargs=expected_kwargs,
            expected_result=expected_result,
        )

    def verify_delete(
        self,
        test_method,
        resource_type,
        ignore_missing=True,
        *,
        method_args=None,
        method_kwargs=None,
        expected_args=None,
        expected_kwargs=None,
        mock_method="openstack.proxy.Proxy._delete",
    ):
        if method_args is None:
            method_args = ['resource_id']
        if method_kwargs is None:
            method_kwargs = {}
        method_kwargs["ignore_missing"] = ignore_missing
        if expected_args is None:
            expected_args = method_args.copy()
        if expected_kwargs is None:
            expected_kwargs = method_kwargs.copy()

        self._verify(
            mock_method,
            test_method,
            method_args=method_args,
            method_kwargs=method_kwargs,
            expected_args=[resource_type] + expected_args,
            expected_kwargs=expected_kwargs,
        )

    def verify_get(
        self,
        test_method,
        resource_type,
        requires_id=False,
        base_path=None,
        *,
        method_args=None,
        method_kwargs=None,
        expected_args=None,
        expected_kwargs=None,
        mock_method="openstack.proxy.Proxy._get",
    ):
        if method_args is None:
            method_args = ['resource_id']
        if method_kwargs is None:
            method_kwargs = {}
        if expected_args is None:
            expected_args = method_args.copy()
        if expected_kwargs is None:
            expected_kwargs = method_kwargs.copy()

        self._verify(
            mock_method,
            test_method,
            method_args=method_args,
            method_kwargs=method_kwargs,
            expected_args=[resource_type] + expected_args,
            expected_kwargs=expected_kwargs,
        )

    def verify_get_overrided(self, proxy, resource_type, patch_target):
        with mock.patch(patch_target, autospec=True) as res:
            proxy._get_resource = mock.Mock(return_value=res)
            proxy._get(resource_type)
            res.fetch.assert_called_once_with(
                proxy,
                requires_id=True,
                base_path=None,
                error_message=mock.ANY,
                skip_cache=False,
            )

    def verify_head(
        self,
        test_method,
        resource_type,
        base_path=None,
        *,
        method_args=None,
        method_kwargs=None,
        expected_args=None,
        expected_kwargs=None,
        mock_method="openstack.proxy.Proxy._head",
    ):
        if method_args is None:
            method_args = ['resource_id']
        if method_kwargs is None:
            method_kwargs = {}
        expected_args = expected_args or method_args.copy()
        expected_kwargs = expected_kwargs or method_kwargs.copy()

        self._verify(
            mock_method,
            test_method,
            method_args=method_args,
            method_kwargs=method_kwargs,
            expected_args=[resource_type] + expected_args,
            expected_kwargs=expected_kwargs,
        )

    def verify_find(
        self,
        test_method,
        resource_type,
        name_or_id='resource_name',
        ignore_missing=True,
        *,
        method_args=None,
        method_kwargs=None,
        expected_args=None,
        expected_kwargs=None,
        mock_method="openstack.proxy.Proxy._find",
    ):
        method_args = [name_or_id] + (method_args or [])
        method_kwargs = method_kwargs or {}
        method_kwargs["ignore_missing"] = ignore_missing
        expected_args = expected_args or method_args.copy()
        expected_kwargs = expected_kwargs or method_kwargs.copy()

        self._verify(
            mock_method,
            test_method,
            method_args=method_args,
            method_kwargs=method_kwargs,
            expected_args=[resource_type] + expected_args,
            expected_kwargs=expected_kwargs,
        )

    def verify_list(
        self,
        test_method,
        resource_type,
        paginated=None,
        base_path=None,
        *,
        method_args=None,
        method_kwargs=None,
        expected_args=None,
        expected_kwargs=None,
        mock_method="openstack.proxy.Proxy._list",
    ):
        if method_args is None:
            method_args = []
        if method_kwargs is None:
            method_kwargs = {}
        if paginated is not None:
            method_kwargs["paginated"] = paginated
        if expected_args is None:
            expected_args = method_args.copy()
        if expected_kwargs is None:
            expected_kwargs = method_kwargs.copy()
        if base_path is not None:
            expected_kwargs["base_path"] = base_path

        self._verify(
            mock_method,
            test_method,
            method_args=method_args,
            method_kwargs=method_kwargs,
            expected_args=[resource_type] + expected_args,
            expected_kwargs=expected_kwargs,
        )

    def verify_update(
        self,
        test_method,
        resource_type,
        base_path=None,
        *,
        method_args=None,
        method_kwargs=None,
        expected_args=None,
        expected_kwargs=None,
        expected_result="result",
        mock_method="openstack.proxy.Proxy._update",
    ):
        if method_args is None:
            method_args = ['resource_id']
        if method_kwargs is None:
            method_kwargs = {"x": 1, "y": 2, "z": 3}
        method_kwargs["base_path"] = base_path
        if expected_args is None:
            expected_args = method_args.copy()
        if expected_kwargs is None:
            expected_kwargs = method_kwargs.copy()

        self._verify(
            mock_method,
            test_method,
            method_args=method_args,
            method_kwargs=method_kwargs,
            expected_args=[resource_type] + expected_args,
            expected_kwargs=expected_kwargs,
        )

    def verify_wait_for_status(
        self,
        test_method,
        mock_method="openstack.resource.wait_for_status",
        **kwargs,
    ):
        self._verify(mock_method, test_method, **kwargs)
