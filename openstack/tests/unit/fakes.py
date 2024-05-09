# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
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

import json
from unittest import mock

import requests


class FakeTransport(mock.Mock):
    RESPONSE = mock.Mock('200 OK')

    def __init__(self):
        super().__init__()
        self.request = mock.Mock()
        self.request.return_value = self.RESPONSE


class FakeAuthenticator(mock.Mock):
    TOKEN = 'fake_token'
    ENDPOINT = 'http://www.example.com/endpoint'

    def __init__(self):
        super().__init__()
        self.get_token = mock.Mock()
        self.get_token.return_value = self.TOKEN
        self.get_endpoint = mock.Mock()
        self.get_endpoint.return_value = self.ENDPOINT


class FakeResponse(requests.Response):
    def __init__(
        self, headers=None, status_code=200, data=None, encoding=None
    ):
        super().__init__()

        headers = headers or {}

        self.status_code = status_code

        self.headers.update(headers)
        self._content = json.dumps(data)
        if not isinstance(self._content, bytes):
            self._content = self._content.encode()
