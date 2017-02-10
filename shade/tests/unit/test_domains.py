# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import uuid

import testtools
from testtools import matchers

import shade
from shade.tests.unit import base
from shade.tests import fakes


domain_obj = fakes.FakeDomain(
    id='1',
    name='a-domain',
    description='A wonderful keystone domain',
    enabled=True,
)


_DomainData = collections.namedtuple(
    'DomainData',
    'domain_id, domain_name, description, json_response, '
    'json_request')


class TestDomains(base.RequestsMockTestCase):

    def get_mock_url(self, service_type='identity',
                     interface='admin', resource='domains',
                     append=None, base_url_append='v3'):
        return super(TestDomains, self).get_mock_url(
            service_type=service_type, interface=interface, resource=resource,
            append=append, base_url_append=base_url_append)

    def _get_domain_data(self, domain_name=None, description=None,
                         enabled=None):
        domain_id = uuid.uuid4().hex
        domain_name = domain_name or self.getUniqueString('domainName')
        response = {'id': domain_id, 'name': domain_name}
        request = {'name': domain_name}
        if enabled is not None:
            request['enabled'] = bool(enabled)
            response['enabled'] = bool(enabled)
        if description:
            response['description'] = description
            request['description'] = description
        response.setdefault('enabled', True)
        return _DomainData(domain_id, domain_name, description,
                           {'domain': response}, {'domain': request})

    def test_list_domains(self):
        self._add_discovery_uri_call()
        domain_data = self._get_domain_data()
        self.register_uri(
            'GET', self.get_mock_url(), status_code=200,
            json={'domains': [domain_data.json_response['domain']]})
        domains = self.op_cloud.list_domains()
        self.assertThat(len(domains), matchers.Equals(1))
        self.assertThat(domains[0].name,
                        matchers.Equals(domain_data.domain_name))
        self.assertThat(domains[0].id,
                        matchers.Equals(domain_data.domain_id))
        self.assert_calls()

    def test_get_domain(self):
        self._add_discovery_uri_call()
        domain_data = self._get_domain_data()
        self.register_uri(
            'GET', self.get_mock_url(append=[domain_data.domain_id]),
            status_code=200,
            json=domain_data.json_response)
        domain = self.op_cloud.get_domain(domain_id=domain_data.domain_id)
        self.assertThat(domain.id, matchers.Equals(domain_data.domain_id))
        self.assertThat(domain.name, matchers.Equals(domain_data.domain_name))
        self.assert_calls()

    def test_get_domain_with_name_or_id(self):
        self._add_discovery_uri_call()
        domain_data = self._get_domain_data()
        self.register_uri(
            'GET', self.get_mock_url(), status_code=200,
            json={'domains': [domain_data.json_response['domain']]})
        self.register_uri(
            'GET', self.get_mock_url(), status_code=200,
            json={'domains': [domain_data.json_response['domain']]})
        domain = self.op_cloud.get_domain(name_or_id=domain_data.domain_id)
        domain_by_name = self.op_cloud.get_domain(
            name_or_id=domain_data.domain_name)
        self.assertThat(domain.id, matchers.Equals(domain_data.domain_id))
        self.assertThat(domain.name, matchers.Equals(domain_data.domain_name))
        self.assertThat(domain_by_name.id,
                        matchers.Equals(domain_data.domain_id))
        self.assertThat(domain_by_name.name,
                        matchers.Equals(domain_data.domain_name))
        self.assert_calls()

    def test_create_domain(self):
        self._add_discovery_uri_call()
        domain_data = self._get_domain_data(description=uuid.uuid4().hex,
                                            enabled=True)
        self.register_uri(
            'POST',
            self.get_mock_url(),
            status_code=200,
            json=domain_data.json_response,
            validate=dict(json=domain_data.json_request))
        self.register_uri(
            'GET',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=200,
            json=domain_data.json_response)
        domain = self.op_cloud.create_domain(
            domain_data.domain_name, domain_data.description)
        self.assertThat(domain.id, matchers.Equals(domain_data.domain_id))
        self.assertThat(domain.name, matchers.Equals(domain_data.domain_name))
        self.assertThat(
            domain.description, matchers.Equals(domain_data.description))
        self.assert_calls()

    def test_create_domain_exception(self):
        self._add_discovery_uri_call()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Failed to create domain domain_name"
        ):
            self.register_uri(
                'POST',
                self.get_mock_url(),
                status_code=409)
            self.op_cloud.create_domain('domain_name')
        self.assert_calls()

    def test_delete_domain(self):
        self._add_discovery_uri_call()
        domain_data = self._get_domain_data()
        new_resp = domain_data.json_response.copy()
        new_resp['domain']['enabled'] = False
        self.register_uri(
            'PATCH',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=200,
            json=new_resp,
            validate={'domain': {'enabled': False}})
        self.register_uri(
            'GET',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=200,
            json=new_resp)
        self.register_uri(
            'DELETE',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=204)
        self.op_cloud.delete_domain(domain_data.domain_id)
        self.assert_calls()

    def test_delete_domain_name_or_id(self):
        self._add_discovery_uri_call()
        domain_data = self._get_domain_data()
        new_resp = domain_data.json_response.copy()
        new_resp['domain']['enabled'] = False
        self.register_uri(
            'GET',
            self.get_mock_url(),
            status_code=200,
            json={'domains': [domain_data.json_response['domain']]})
        self.register_uri(
            'PATCH',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=200,
            json=new_resp,
            validate={'domain': {'enabled': False}})
        self.register_uri(
            'GET',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=200,
            json=new_resp)
        self.register_uri(
            'DELETE',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=204)
        self.op_cloud.delete_domain(name_or_id=domain_data.domain_id)
        self.assert_calls()

    def test_delete_domain_exception(self):
        # NOTE(notmorgan): This test does not reflect the case where the domain
        # cannot be updated to be disabled, Shade raises that as an unable
        # to update domain even though it is called via delete_domain. This
        # should be fixed in shade to catch either a failure on PATCH,
        # subsequent GET, or DELETE call(s).
        self._add_discovery_uri_call()
        domain_data = self._get_domain_data()
        new_resp = domain_data.json_response.copy()
        new_resp['domain']['enabled'] = False
        self.register_uri(
            'PATCH',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=200,
            json=new_resp,
            validate={'domain': {'enabled': False}})
        self.register_uri(
            'GET',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=200,
            json=new_resp)
        self.register_uri(
            'DELETE',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=404)
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Failed to delete domain %s" % domain_data.domain_id
        ):
            self.op_cloud.delete_domain(domain_data.domain_id)
        self.assert_calls()

    def test_update_domain(self):
        self._add_discovery_uri_call()
        domain_data = self._get_domain_data(
            description=self.getUniqueString('domainDesc'))
        self.register_uri(
            'PATCH',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=200,
            json=domain_data.json_response,
            validate=dict(json=domain_data.json_request))
        self.register_uri(
            'GET',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=200,
            json=domain_data.json_response)
        domain = self.op_cloud.update_domain(
            domain_data.domain_id,
            name=domain_data.domain_name,
            description=domain_data.description)
        self.assertThat(domain.id, matchers.Equals(domain_data.domain_id))
        self.assertThat(domain.name, matchers.Equals(domain_data.domain_name))
        self.assertThat(
            domain.description, matchers.Equals(domain_data.description))
        self.assert_calls()

    def test_update_domain_name_or_id(self):
        self._add_discovery_uri_call()
        domain_data = self._get_domain_data(
            description=self.getUniqueString('domainDesc'))
        self.register_uri(
            'GET',
            self.get_mock_url(), status_code=200,
            json={'domains': [domain_data.json_response['domain']]})
        self.register_uri(
            'PATCH',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=200,
            json=domain_data.json_response,
            validate=dict(json=domain_data.json_request))
        self.register_uri(
            'GET',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=200,
            json=domain_data.json_response)
        domain = self.op_cloud.update_domain(
            name_or_id=domain_data.domain_id,
            name=domain_data.domain_name,
            description=domain_data.description)
        self.assertThat(domain.id, matchers.Equals(domain_data.domain_id))
        self.assertThat(domain.name, matchers.Equals(domain_data.domain_name))
        self.assertThat(
            domain.description, matchers.Equals(domain_data.description))
        self.assert_calls()

    def test_update_domain_exception(self):
        self._add_discovery_uri_call()
        domain_data = self._get_domain_data(
            description=self.getUniqueString('domainDesc'))
        self.register_uri(
            'PATCH',
            self.get_mock_url(append=[domain_data.domain_id]),
            status_code=409)
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Error in updating domain %s" % domain_data.domain_id
        ):
            self.op_cloud.delete_domain(domain_data.domain_id)
        self.assert_calls()
