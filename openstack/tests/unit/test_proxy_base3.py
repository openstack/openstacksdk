#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
import inspect
import json
import os

import mock

from openstack import session
from openstack.tests.unit import base


class BaseProxyTestCase(base.TestCase):
    def __init__(self, *args, **kwargs):
        proxy_class = kwargs.pop('proxy_class')
        service_class = kwargs.pop('service_class')
        super(BaseProxyTestCase, self).__init__(*args, **kwargs)
        self.response = mock.Mock(headers=mock.PropertyMock(return_value={}))
        self.session = mock.Mock(spec=session.Session)
        self.session.create = mock.Mock(return_value=self.response)
        self.session.get = mock.Mock(return_value=self.response)
        self.session.put = mock.Mock(return_value=self.response)
        self.session.patch = mock.Mock(return_value=self.response)
        self.session.post = mock.Mock(return_value=self.response)
        self.session.delete = mock.Mock(return_value=self.response)
        self.session.head = mock.Mock(return_value=self.response)
        self.proxy = proxy_class(self.session)
        self.service = service_class()

        self.file = inspect.getfile(self.__class__)
        self.current_dir = os.path.dirname(self.file)

    def setUp(self):
        super(BaseProxyTestCase, self).setUp()

    def get_file_content(self, filename):
        file_path = os.path.join(self.current_dir,
                                 'data_files',
                                 filename)
        with open(file_path) as data_file:
            return json.loads(data_file.read())

    def mock_response_json_file_values(self, filename):
        _json = self.get_file_content(filename)
        self.response.json.return_value = _json
        return _json

    def mock_response_json_values(self, values):
        self.response.json.return_value = values

    def mock_response_header_values(self, values):
        self.response.headers = values

    def assert_session_list_with(self,
                                 uri,
                                 params={},
                                 header={'Accept': 'application/json'}):
        self.session.get.assert_called_once_with(
            uri,
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
            headers=header,
            params=params
        )

    def assert_session_get_with(self, uri):
        self.session.get.assert_called_once_with(
            uri,
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override()
        )

    def assert_session_post_with(self, uri, json, headers={}):
        self.session.post.assert_called_once_with(
            uri,
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
            headers=headers,
            json=json
        )

    def assert_session_put_with(self, uri, json, header={}):
        self.session.put.assert_called_once_with(
            uri,
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
            headers=header,
            json=json
        )

    def assert_session_patch_with(self, uri, json, header={}):
        self.session.patch.assert_called_once_with(
            uri,
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
            headers=header,
            json=json
        )

    def assert_session_delete(self, uri, params=None):
        self.session.delete.assert_called_once_with(
            uri,
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
            headers={'Accept': ''},
            params=params
        )
