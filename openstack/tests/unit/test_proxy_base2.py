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

from openstack.tests.unit import base


class TestProxyBase(base.TestCase):
    # object_store makes calls with container= rather than
    # path_args=dict(container= because container needs to wind up
    # in the uri components.
    kwargs_to_path_args = True

    def setUp(self):
        super(TestProxyBase, self).setUp()
        self.session = mock.Mock()

    def _add_path_args_for_verify(self, path_args, method_args,
                                  expected_kwargs, value=None):
        if path_args is not None:
            if value is None:
                for key in path_args:
                    method_args.append(path_args[key])
            expected_kwargs['path_args'] = path_args

    def _verify(self, mock_method, test_method,
                method_args=None, method_kwargs=None,
                expected_args=None, expected_kwargs=None,
                expected_result=None):
        with mock.patch(mock_method) as mocked:
            mocked.return_value = expected_result
            if any([method_args, method_kwargs,
                    expected_args, expected_kwargs]):
                method_args = method_args or ()
                method_kwargs = method_kwargs or {}
                expected_args = expected_args or ()
                expected_kwargs = expected_kwargs or {}

                self.assertEqual(expected_result, test_method(*method_args,
                                 **method_kwargs))
                mocked.assert_called_with(test_method.__self__,
                                          *expected_args, **expected_kwargs)
            else:
                self.assertEqual(expected_result, test_method())
                mocked.assert_called_with(test_method.__self__)

    # NOTE(briancurtin): This is a duplicate version of _verify that is
    # temporarily here while we shift APIs. The difference is that
    # calls from the Proxy classes aren't going to be going directly into
    # the Resource layer anymore, so they don't pass in the session which
    # was tested in assert_called_with.
    # This is being done in lieu of adding logic and complicating
    # the _verify method. It will be removed once there is one API to
    # be verifying.
    def _verify2(self, mock_method, test_method,
                 method_args=None, method_kwargs=None, method_result=None,
                 expected_args=None, expected_kwargs=None,
                 expected_result=None):
        with mock.patch(mock_method) as mocked:
            mocked.return_value = expected_result
            if any([method_args, method_kwargs,
                    expected_args, expected_kwargs]):
                method_args = method_args or ()
                method_kwargs = method_kwargs or {}
                expected_args = expected_args or ()
                expected_kwargs = expected_kwargs or {}

                if method_result:
                    self.assertEqual(method_result, test_method(*method_args,
                                     **method_kwargs))
                else:
                    self.assertEqual(expected_result, test_method(*method_args,
                                     **method_kwargs))
                mocked.assert_called_with(*expected_args, **expected_kwargs)
            else:
                self.assertEqual(expected_result, test_method())
                mocked.assert_called_with(test_method.__self__)

    def verify_create(self, test_method, resource_type,
                      mock_method="openstack.proxy.Proxy._create",
                      expected_result="result", **kwargs):
        the_kwargs = {"x": 1, "y": 2, "z": 3}
        method_kwargs = kwargs.pop("method_kwargs", the_kwargs)
        expected_args = [resource_type]
        expected_kwargs = kwargs.pop("expected_kwargs", the_kwargs)

        self._verify2(mock_method, test_method,
                      expected_result=expected_result,
                      method_kwargs=method_kwargs,
                      expected_args=expected_args,
                      expected_kwargs=expected_kwargs,
                      **kwargs)

    def verify_delete(self, test_method, resource_type, ignore,
                      input_path_args=None, expected_path_args=None,
                      method_kwargs=None, expected_args=None,
                      expected_kwargs=None,
                      mock_method="openstack.proxy.Proxy._delete"):
        method_args = ["resource_or_id"]
        method_kwargs = method_kwargs or {}
        method_kwargs["ignore_missing"] = ignore
        if isinstance(input_path_args, dict):
            for key in input_path_args:
                method_kwargs[key] = input_path_args[key]
        elif isinstance(input_path_args, list):
            method_args = input_path_args
        expected_kwargs = expected_kwargs or {}
        expected_kwargs["ignore_missing"] = ignore
        if expected_path_args:
            expected_kwargs.update(expected_path_args)
        expected_args = expected_args or [resource_type, "resource_or_id"]
        self._verify2(mock_method, test_method,
                      method_args=method_args,
                      method_kwargs=method_kwargs,
                      expected_args=expected_args,
                      expected_kwargs=expected_kwargs)

    def verify_get(self, test_method, resource_type, value=None, args=None,
                   mock_method="openstack.proxy.Proxy._get",
                   ignore_value=False, **kwargs):
        the_value = value
        if value is None:
            the_value = [] if ignore_value else ["value"]
        expected_args = kwargs.pop("expected_args", [])
        expected_kwargs = kwargs.pop("expected_kwargs", {})
        method_kwargs = kwargs.pop("method_kwargs", kwargs)
        if args:
            expected_kwargs["args"] = args
        if kwargs and self.kwargs_to_path_args:
            expected_kwargs["path_args"] = kwargs
        if not expected_args:
            expected_args = [resource_type] + the_value
        self._verify2(mock_method, test_method,
                      method_args=the_value,
                      method_kwargs=method_kwargs or {},
                      expected_args=expected_args,
                      expected_kwargs=expected_kwargs)

    def verify_head(self, test_method, resource_type,
                    mock_method="openstack.proxy.Proxy._head",
                    value=None, **kwargs):
        the_value = [value] if value is not None else []
        if self.kwargs_to_path_args:
            expected_kwargs = {"path_args": kwargs} if kwargs else {}
        else:
            expected_kwargs = kwargs or {}
        self._verify2(mock_method, test_method,
                      method_args=the_value,
                      method_kwargs=kwargs,
                      expected_args=[resource_type] + the_value,
                      expected_kwargs=expected_kwargs)

    def verify_find(self, test_method, resource_type, value=None,
                    mock_method="openstack.proxy.Proxy._find",
                    path_args=None, **kwargs):
        method_args = value or ["name_or_id"]
        expected_kwargs = {}

        self._add_path_args_for_verify(path_args, method_args, expected_kwargs,
                                       value=value)

        # TODO(briancurtin): if sub-tests worked in this mess of
        # test dependencies, the following would be a lot easier to work with.
        expected_kwargs["ignore_missing"] = False
        self._verify2(mock_method, test_method,
                      method_args=method_args + [False],
                      expected_args=[resource_type, "name_or_id"],
                      expected_kwargs=expected_kwargs,
                      expected_result="result",
                      **kwargs)

        expected_kwargs["ignore_missing"] = True
        self._verify2(mock_method, test_method,
                      method_args=method_args + [True],
                      expected_args=[resource_type, "name_or_id"],
                      expected_kwargs=expected_kwargs,
                      expected_result="result",
                      **kwargs)

    def verify_list(self, test_method, resource_type, paginated=False,
                    mock_method="openstack.proxy.Proxy._list",
                    **kwargs):
        expected_kwargs = kwargs.pop("expected_kwargs", {})
        expected_kwargs.update({"paginated": paginated})
        method_kwargs = kwargs.pop("method_kwargs", {})
        self._verify2(mock_method, test_method,
                      method_kwargs=method_kwargs,
                      expected_args=[resource_type],
                      expected_kwargs=expected_kwargs,
                      expected_result=["result"],
                      **kwargs)

    def verify_list_no_kwargs(self, test_method, resource_type,
                              paginated=False,
                              mock_method="openstack.proxy.Proxy._list"):
        self._verify2(mock_method, test_method,
                      method_kwargs={},
                      expected_args=[resource_type],
                      expected_kwargs={"paginated": paginated},
                      expected_result=["result"])

    def verify_update(self, test_method, resource_type, value=None,
                      mock_method="openstack.proxy.Proxy._update",
                      expected_result="result", path_args=None, **kwargs):
        method_args = value or ["resource_or_id"]
        method_kwargs = {"x": 1, "y": 2, "z": 3}
        expected_args = kwargs.pop("expected_args", ["resource_or_id"])
        expected_kwargs = method_kwargs.copy()

        self._add_path_args_for_verify(path_args, method_args, expected_kwargs,
                                       value=value)

        self._verify2(mock_method, test_method,
                      expected_result=expected_result,
                      method_args=method_args,
                      method_kwargs=method_kwargs,
                      expected_args=[resource_type] + expected_args,
                      expected_kwargs=expected_kwargs,
                      **kwargs)

    def verify_wait_for_status(
            self, test_method,
            mock_method="openstack.resource.wait_for_status", **kwargs):
        self._verify(mock_method, test_method, **kwargs)
