# Copyright 2019 Red Hat, Inc.
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

import uuid

import fixtures
from keystoneauth1.fixture import v2
from keystoneauth1.fixture import v3
import os_service_types

_service_type_manager = os_service_types.ServiceTypes()

_SUBURL_TEMPLATES = {
    'public': 'https://example.com/{service_type}',
    'internal': 'https://internal.example.com/{service_type}',
    'admin': 'https://example.com/{service_type}',
}
_ENDPOINT_TEMPLATES = {
    'public': 'https://{service_type}.example.com',
    'internal': 'https://internal.{service_type}.example.com',
    'admin': 'https://{service_type}.example.com',
}


class ConnectionFixture(fixtures.Fixture):

    _suffixes = {
        'baremetal': '/',
        'block-storage': '/{project_id}',
        'compute': '/v2.1/',
        'container-infrastructure-management': '/v1',
        'object-store': '/v1/{project_id}',
        'orchestration': '/v1/{project_id}',
        'volumev2': '/v2/{project_id}',
        'volumev3': '/v3/{project_id}',
    }

    def __init__(self, suburl=False, project_id=None, *args, **kwargs):
        super(ConnectionFixture, self).__init__(*args, **kwargs)
        self._endpoint_templates = _ENDPOINT_TEMPLATES
        if suburl:
            self.use_suburl()
        self.project_id = project_id or uuid.uuid4().hex.replace('-', '')
        self.build_tokens()

    def use_suburl(self):
        self._endpoint_templates = _SUBURL_TEMPLATES

    def _get_endpoint_templates(self, service_type, alias=None, v2=False):
        templates = {}
        for k, v in self._endpoint_templates.items():
            suffix = self._suffixes.get(
                alias, self._suffixes.get(service_type, ''))
            # For a keystone v2 catalog, we want to list the
            # versioned endpoint in the catalog, because that's
            # more likely how those were deployed.
            if v2:
                suffix = '/v2.0'
            templates[k] = (v + suffix).format(
                service_type=service_type,
                project_id=self.project_id,
            )
        return templates

    def _setUp(self):
        pass

    def clear_tokens(self):
        self.v2_token = v2.Token(tenant_id=self.project_id)
        self.v3_token = v3.Token(project_id=self.project_id)

    def build_tokens(self):
        self.clear_tokens()
        for service in _service_type_manager.services:
            service_type = service['service_type']
            if service_type == 'ec2-api':
                continue
            service_name = service['project']
            ets = self._get_endpoint_templates(service_type)
            v3_svc = self.v3_token.add_service(
                service_type, name=service_name)
            v2_svc = self.v2_token.add_service(
                service_type, name=service_name)
            v3_svc.add_standard_endpoints(region='RegionOne', **ets)
            if service_type == 'identity':
                ets = self._get_endpoint_templates(service_type, v2=True)
            v2_svc.add_endpoint(region='RegionOne', **ets)
            for alias in service.get('aliases', []):
                ets = self._get_endpoint_templates(service_type, alias=alias)
                v3_svc = self.v3_token.add_service(alias, name=service_name)
                v2_svc = self.v2_token.add_service(alias, name=service_name)
                v3_svc.add_standard_endpoints(region='RegionOne', **ets)
                v2_svc.add_endpoint(region='RegionOne', **ets)

    def _cleanup(self):
        pass
