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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import openstack.cloud
from openstack.tests.unit import base


class TestOpenStackCloudOperatorNoAuth(base.TestCase):
    def setUp(self):
        """Setup Noauth OpenStackCloud tests

        Setup the test to utilize no authentication and an endpoint
        URL in the auth data.  This is permits testing of the basic
        mechanism that enables Ironic noauth mode to be utilized with
        Shade.

        Uses base.TestCase instead of IronicTestCase because
        we need to do completely different things with discovery.
        """
        super(TestOpenStackCloudOperatorNoAuth, self).setUp()
        # By clearing the URI registry, we remove all calls to a keystone
        # catalog or getting a token
        self._uri_registry.clear()
        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     service_type='baremetal', base_url_append='v1'),
                 json={'id': 'v1',
                       'links': [{"href": "https://bare-metal.example.com/v1",
                                  "rel": "self"}]}),
            dict(method='GET',
                 uri=self.get_mock_url(
                     service_type='baremetal', base_url_append='v1',
                     resource='nodes'),
                 json={'nodes': []}),
        ])

    def test_ironic_noauth_none_auth_type(self):
        """Test noauth selection for Ironic in OpenStackCloud

        The new way of doing this is with the keystoneauth none plugin.
        """
        # NOTE(TheJulia): When we are using the python-ironicclient
        # library, the library will automatically prepend the URI path
        # with 'v1'. As such, since we are overriding the endpoint,
        # we must explicitly do the same as we move away from the
        # client library.
        self.cloud_noauth = openstack.connect(
            auth_type='none',
            baremetal_endpoint_override="https://bare-metal.example.com/v1")

        self.cloud_noauth.list_machines()

        self.assert_calls()

    def test_ironic_noauth_auth_endpoint(self):
        """Test noauth selection for Ironic in OpenStackCloud

        Sometimes people also write clouds.yaml files that look like this:

        ::
          clouds:
            bifrost:
              auth_type: "none"
              endpoint: https://bare-metal.example.com
        """
        self.cloud_noauth = openstack.connect(
            auth_type='none',
            endpoint='https://bare-metal.example.com/v1',
        )

        self.cloud_noauth.list_machines()

        self.assert_calls()

    def test_ironic_noauth_admin_token_auth_type(self):
        """Test noauth selection for Ironic in OpenStackCloud

        The old way of doing this was to abuse admin_token.
        """
        self.cloud_noauth = openstack.connect(
            auth_type='admin_token',
            auth=dict(
                endpoint='https://bare-metal.example.com/v1',
                token='ignored'))

        self.cloud_noauth.list_machines()

        self.assert_calls()


class TestOpenStackCloudOperatorNoAuthUnversioned(base.TestCase):
    def setUp(self):
        """Setup Noauth OpenStackCloud tests for unversioned endpoints

        Setup the test to utilize no authentication and an endpoint
        URL in the auth data.  This is permits testing of the basic
        mechanism that enables Ironic noauth mode to be utilized with
        Shade.

        Uses base.TestCase instead of IronicTestCase because
        we need to do completely different things with discovery.
        """
        super(TestOpenStackCloudOperatorNoAuthUnversioned, self).setUp()
        # By clearing the URI registry, we remove all calls to a keystone
        # catalog or getting a token
        self._uri_registry.clear()
        self.register_uris([
            dict(method='GET',
                 uri='https://bare-metal.example.com/',
                 json={
                     "default_version": {
                         "status": "CURRENT",
                         "min_version": "1.1",
                         "version": "1.46",
                         "id": "v1",
                         "links": [{
                             "href": "https://bare-metal.example.com/v1",
                             "rel": "self"
                         }]},
                     "versions": [{
                         "status": "CURRENT",
                         "min_version": "1.1",
                         "version": "1.46",
                         "id": "v1",
                         "links": [{
                             "href": "https://bare-metal.example.com/v1",
                             "rel": "self"
                         }]}],
                     "name": "OpenStack Ironic API",
                     "description": "Ironic is an OpenStack project."
                 }),
            dict(method='GET',
                 uri=self.get_mock_url(
                     service_type='baremetal', base_url_append='v1'),
                 json={
                     "media_types": [{
                         "base": "application/json",
                         "type": "application/vnd.openstack.ironic.v1+json"
                     }],
                     "links": [{
                         "href": "https://bare-metal.example.com/v1",
                         "rel": "self"
                     }],
                     "ports": [{
                         "href": "https://bare-metal.example.com/v1/ports/",
                         "rel": "self"
                     }, {
                         "href": "https://bare-metal.example.com/ports/",
                         "rel": "bookmark"
                     }],
                     "nodes": [{
                         "href": "https://bare-metal.example.com/v1/nodes/",
                         "rel": "self"
                     }, {
                         "href": "https://bare-metal.example.com/nodes/",
                         "rel": "bookmark"
                     }],
                     "id": "v1"
                 }),
            dict(method='GET',
                 uri=self.get_mock_url(
                     service_type='baremetal', base_url_append='v1',
                     resource='nodes'),
                 json={'nodes': []}),
        ])

    def test_ironic_noauth_none_auth_type(self):
        """Test noauth selection for Ironic in OpenStackCloud

        The new way of doing this is with the keystoneauth none plugin.
        """
        # NOTE(TheJulia): When we are using the python-ironicclient
        # library, the library will automatically prepend the URI path
        # with 'v1'. As such, since we are overriding the endpoint,
        # we must explicitly do the same as we move away from the
        # client library.
        self.cloud_noauth = openstack.connect(
            auth_type='none',
            baremetal_endpoint_override="https://bare-metal.example.com")

        self.cloud_noauth.list_machines()

        self.assert_calls()

    def test_ironic_noauth_auth_endpoint(self):
        """Test noauth selection for Ironic in OpenStackCloud

        Sometimes people also write clouds.yaml files that look like this:

        ::
          clouds:
            bifrost:
              auth_type: "none"
              endpoint: https://bare-metal.example.com
        """
        self.cloud_noauth = openstack.connect(
            auth_type='none',
            endpoint='https://bare-metal.example.com/',
        )

        self.cloud_noauth.list_machines()

        self.assert_calls()
