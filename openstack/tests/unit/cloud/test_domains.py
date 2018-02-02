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

import uuid

import testtools
from testtools import matchers

import openstack.cloud
from openstack.tests.unit import base


class TestDomains(base.TestCase):

    def get_mock_url(self, service_type='identity',
                     interface='admin', resource='domains',
                     append=None, base_url_append='v3'):
        return super(TestDomains, self).get_mock_url(
            service_type=service_type, interface=interface, resource=resource,
            append=append, base_url_append=base_url_append)

    def test_list_domains(self):
        domain_data = self._get_domain_data()
        self.register_uris([
            dict(method='GET', uri=self.get_mock_url(), status_code=200,
                 json={'domains': [domain_data.json_response['domain']]})])
        domains = self.cloud.list_domains()
        self.assertThat(len(domains), matchers.Equals(1))
        self.assertThat(domains[0].name,
                        matchers.Equals(domain_data.domain_name))
        self.assertThat(domains[0].id,
                        matchers.Equals(domain_data.domain_id))
        self.assert_calls()

    def test_get_domain(self):
        domain_data = self._get_domain_data()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(append=[domain_data.domain_id]),
                 status_code=200,
                 json=domain_data.json_response)])
        domain = self.cloud.get_domain(domain_id=domain_data.domain_id)
        self.assertThat(domain.id, matchers.Equals(domain_data.domain_id))
        self.assertThat(domain.name, matchers.Equals(domain_data.domain_name))
        self.assert_calls()

    def test_get_domain_with_name_or_id(self):
        domain_data = self._get_domain_data()
        response = {'domains': [domain_data.json_response['domain']]}
        self.register_uris([
            dict(method='GET', uri=self.get_mock_url(), status_code=200,
                 json=response),
            dict(method='GET', uri=self.get_mock_url(), status_code=200,
                 json=response)])
        domain = self.cloud.get_domain(name_or_id=domain_data.domain_id)
        domain_by_name = self.cloud.get_domain(
            name_or_id=domain_data.domain_name)
        self.assertThat(domain.id, matchers.Equals(domain_data.domain_id))
        self.assertThat(domain.name, matchers.Equals(domain_data.domain_name))
        self.assertThat(domain_by_name.id,
                        matchers.Equals(domain_data.domain_id))
        self.assertThat(domain_by_name.name,
                        matchers.Equals(domain_data.domain_name))
        self.assert_calls()

    def test_create_domain(self):
        domain_data = self._get_domain_data(description=uuid.uuid4().hex,
                                            enabled=True)
        self.register_uris([
            dict(method='POST', uri=self.get_mock_url(), status_code=200,
                 json=domain_data.json_response,
                 validate=dict(json=domain_data.json_request))])
        domain = self.cloud.create_domain(
            domain_data.domain_name, domain_data.description)
        self.assertThat(domain.id, matchers.Equals(domain_data.domain_id))
        self.assertThat(domain.name, matchers.Equals(domain_data.domain_name))
        self.assertThat(
            domain.description, matchers.Equals(domain_data.description))
        self.assert_calls()

    def test_create_domain_exception(self):
        domain_data = self._get_domain_data(domain_name='domain_name',
                                            enabled=True)
        with testtools.ExpectedException(
            openstack.cloud.OpenStackCloudBadRequest,
            "Failed to create domain domain_name"
        ):
            self.register_uris([
                dict(method='POST', uri=self.get_mock_url(), status_code=400,
                     json=domain_data.json_response,
                     validate=dict(json=domain_data.json_request))])
            self.cloud.create_domain('domain_name')
        self.assert_calls()

    def test_delete_domain(self):
        domain_data = self._get_domain_data()
        new_resp = domain_data.json_response.copy()
        new_resp['domain']['enabled'] = False
        domain_resource_uri = self.get_mock_url(append=[domain_data.domain_id])
        self.register_uris([
            dict(method='PATCH', uri=domain_resource_uri, status_code=200,
                 json=new_resp,
                 validate=dict(json={'domain': {'enabled': False}})),
            dict(method='DELETE', uri=domain_resource_uri, status_code=204)])
        self.cloud.delete_domain(domain_data.domain_id)
        self.assert_calls()

    def test_delete_domain_name_or_id(self):
        domain_data = self._get_domain_data()
        new_resp = domain_data.json_response.copy()
        new_resp['domain']['enabled'] = False

        domain_resource_uri = self.get_mock_url(append=[domain_data.domain_id])
        self.register_uris([
            dict(method='GET', uri=self.get_mock_url(), status_code=200,
                 json={'domains': [domain_data.json_response['domain']]}),
            dict(method='PATCH', uri=domain_resource_uri, status_code=200,
                 json=new_resp,
                 validate=dict(json={'domain': {'enabled': False}})),
            dict(method='DELETE', uri=domain_resource_uri, status_code=204)])
        self.cloud.delete_domain(name_or_id=domain_data.domain_id)
        self.assert_calls()

    def test_delete_domain_exception(self):
        # NOTE(notmorgan): This test does not reflect the case where the domain
        # cannot be updated to be disabled, Shade raises that as an unable
        # to update domain even though it is called via delete_domain. This
        # should be fixed in shade to catch either a failure on PATCH,
        # subsequent GET, or DELETE call(s).
        domain_data = self._get_domain_data()
        new_resp = domain_data.json_response.copy()
        new_resp['domain']['enabled'] = False
        domain_resource_uri = self.get_mock_url(append=[domain_data.domain_id])
        self.register_uris([
            dict(method='PATCH', uri=domain_resource_uri, status_code=200,
                 json=new_resp,
                 validate=dict(json={'domain': {'enabled': False}})),
            dict(method='DELETE', uri=domain_resource_uri, status_code=404)])
        with testtools.ExpectedException(
            openstack.cloud.OpenStackCloudURINotFound,
            "Failed to delete domain %s" % domain_data.domain_id
        ):
            self.cloud.delete_domain(domain_data.domain_id)
        self.assert_calls()

    def test_update_domain(self):
        domain_data = self._get_domain_data(
            description=self.getUniqueString('domainDesc'))
        domain_resource_uri = self.get_mock_url(append=[domain_data.domain_id])
        self.register_uris([
            dict(method='PATCH', uri=domain_resource_uri, status_code=200,
                 json=domain_data.json_response,
                 validate=dict(json=domain_data.json_request))])
        domain = self.cloud.update_domain(
            domain_data.domain_id,
            name=domain_data.domain_name,
            description=domain_data.description)
        self.assertThat(domain.id, matchers.Equals(domain_data.domain_id))
        self.assertThat(domain.name, matchers.Equals(domain_data.domain_name))
        self.assertThat(
            domain.description, matchers.Equals(domain_data.description))
        self.assert_calls()

    def test_update_domain_name_or_id(self):
        domain_data = self._get_domain_data(
            description=self.getUniqueString('domainDesc'))
        domain_resource_uri = self.get_mock_url(append=[domain_data.domain_id])
        self.register_uris([
            dict(method='GET', uri=self.get_mock_url(), status_code=200,
                 json={'domains': [domain_data.json_response['domain']]}),
            dict(method='PATCH', uri=domain_resource_uri, status_code=200,
                 json=domain_data.json_response,
                 validate=dict(json=domain_data.json_request))])
        domain = self.cloud.update_domain(
            name_or_id=domain_data.domain_id,
            name=domain_data.domain_name,
            description=domain_data.description)
        self.assertThat(domain.id, matchers.Equals(domain_data.domain_id))
        self.assertThat(domain.name, matchers.Equals(domain_data.domain_name))
        self.assertThat(
            domain.description, matchers.Equals(domain_data.description))
        self.assert_calls()

    def test_update_domain_exception(self):
        domain_data = self._get_domain_data(
            description=self.getUniqueString('domainDesc'))
        self.register_uris([
            dict(method='PATCH',
                 uri=self.get_mock_url(append=[domain_data.domain_id]),
                 status_code=409,
                 json=domain_data.json_response,
                 validate=dict(json={'domain': {'enabled': False}}))])
        with testtools.ExpectedException(
            openstack.cloud.OpenStackCloudHTTPError,
            "Error in updating domain %s" % domain_data.domain_id
        ):
            self.cloud.delete_domain(domain_data.domain_id)
        self.assert_calls()
