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

import os
from unittest import mock

import fixtures
from keystoneauth1 import session
from testtools import matchers

from openstack import connection
from openstack import proxy
import openstack.config
from openstack import service_description
from openstack.tests import fakes
from openstack.tests.unit import base
from openstack.tests.unit.fake import fake_service


CONFIG_AUTH_URL = "https://identity.example.com/"
CONFIG_USERNAME = "BozoTheClown"
CONFIG_PASSWORD = "TopSecret"
CONFIG_PROJECT = "TheGrandPrizeGame"
CONFIG_CACERT = "TrustMe"

CLOUD_CONFIG = """
clouds:
  sample-cloud:
    region_name: RegionOne
    auth:
      auth_url: {auth_url}
      username: {username}
      password: {password}
      project_name: {project}
  insecure-cloud:
    auth:
      auth_url: {auth_url}
      username: {username}
      password: {password}
      project_name: {project}
    cacert: {cacert}
    verify: False
  insecure-cloud-alternative-format:
    auth:
      auth_url: {auth_url}
      username: {username}
      password: {password}
      project_name: {project}
    insecure: True
  cacert-cloud:
    auth:
      auth_url: {auth_url}
      username: {username}
      password: {password}
      project_name: {project}
    cacert: {cacert}
  profiled-cloud:
    profile: dummy
    auth:
      username: {username}
      password: {password}
      project_name: {project}
    cacert: {cacert}
""".format(auth_url=CONFIG_AUTH_URL, username=CONFIG_USERNAME,
           password=CONFIG_PASSWORD, project=CONFIG_PROJECT,
           cacert=CONFIG_CACERT)

VENDOR_CONFIG = """
{{
  "name": "dummy",
  "profile": {{
    "auth": {{
      "auth_url": "{auth_url}"
    }},
    "vendor_hook": "openstack.tests.unit.test_connection:vendor_hook"
  }}
}}
""".format(auth_url=CONFIG_AUTH_URL)

PUBLIC_CLOUDS_YAML = """
public-clouds:
  dummy:
    auth:
      auth_url: {auth_url}
    vendor_hook: openstack.tests.unit.test_connection:vendor_hook
""".format(auth_url=CONFIG_AUTH_URL)


class _TestConnectionBase(base.TestCase):

    def setUp(self):
        super(_TestConnectionBase, self).setUp()
        # Create a temporary directory where our test config will live
        # and insert it into the search path via OS_CLIENT_CONFIG_FILE.
        config_dir = self.useFixture(fixtures.TempDir()).path
        config_path = os.path.join(config_dir, "clouds.yaml")

        with open(config_path, "w") as conf:
            conf.write(CLOUD_CONFIG)

        self.useFixture(fixtures.EnvironmentVariable(
            "OS_CLIENT_CONFIG_FILE", config_path))
        self.use_keystone_v2()


class TestConnection(_TestConnectionBase):
    def test_other_parameters(self):
        conn = connection.Connection(cloud='sample-cloud', cert='cert')
        self.assertEqual(conn.session.cert, 'cert')

    def test_session_provided(self):
        mock_session = mock.Mock(spec=session.Session)
        mock_session.auth = mock.Mock()
        mock_session.auth.auth_url = 'https://auth.example.com'
        conn = connection.Connection(session=mock_session, cert='cert')
        self.assertEqual(mock_session, conn.session)
        self.assertEqual('auth.example.com', conn.config.name)

    def test_create_session(self):
        conn = connection.Connection(cloud='sample-cloud')
        self.assertIsNotNone(conn)
        # TODO(mordred) Rework this - we need to provide requests-mock
        # entries for each of the proxies below
        # self.assertEqual('openstack.proxy',
        #                  conn.alarm.__class__.__module__)
        # self.assertEqual('openstack.clustering.v1._proxy',
        #                  conn.clustering.__class__.__module__)
        # self.assertEqual('openstack.compute.v2._proxy',
        #                  conn.compute.__class__.__module__)
        # self.assertEqual('openstack.database.v1._proxy',
        #                  conn.database.__class__.__module__)
        # self.assertEqual('openstack.identity.v2._proxy',
        #                  conn.identity.__class__.__module__)
        # self.assertEqual('openstack.image.v2._proxy',
        #                  conn.image.__class__.__module__)
        # self.assertEqual('openstack.object_store.v1._proxy',
        #                  conn.object_store.__class__.__module__)
        # self.assertEqual('openstack.load_balancer.v2._proxy',
        #                  conn.load_balancer.__class__.__module__)
        # self.assertEqual('openstack.orchestration.v1._proxy',
        #                  conn.orchestration.__class__.__module__)
        # self.assertEqual('openstack.workflow.v2._proxy',
        #                  conn.workflow.__class__.__module__)

    def test_create_unknown_proxy(self):
        self.register_uris([
            self.get_placement_discovery_mock_dict(),
        ])

        def closure():
            return self.cloud.placement

        self.assertThat(
            closure,
            matchers.Warnings(matchers.HasLength(0)))

        self.assertIsInstance(
            self.cloud.placement,
            proxy.Proxy)

        self.assert_calls()

    def test_create_connection_version_param_default(self):
        c1 = connection.Connection(cloud='sample-cloud')
        conn = connection.Connection(session=c1.session)
        self.assertEqual('openstack.identity.v3._proxy',
                         conn.identity.__class__.__module__)

    def test_create_connection_version_param_string(self):
        c1 = connection.Connection(cloud='sample-cloud')
        conn = connection.Connection(
            session=c1.session, identity_api_version='2')
        self.assertEqual('openstack.identity.v2._proxy',
                         conn.identity.__class__.__module__)

    def test_create_connection_version_param_int(self):
        c1 = connection.Connection(cloud='sample-cloud')
        conn = connection.Connection(
            session=c1.session, identity_api_version=3)
        self.assertEqual('openstack.identity.v3._proxy',
                         conn.identity.__class__.__module__)

    def test_create_connection_version_param_bogus(self):
        c1 = connection.Connection(cloud='sample-cloud')
        conn = connection.Connection(
            session=c1.session, identity_api_version='red')
        # TODO(mordred) This is obviously silly behavior
        self.assertEqual('openstack.identity.v3._proxy',
                         conn.identity.__class__.__module__)

    def test_from_config_given_config(self):
        cloud_region = (openstack.config.OpenStackConfig().
                        get_one("sample-cloud"))

        sot = connection.from_config(config=cloud_region)

        self.assertEqual(CONFIG_USERNAME,
                         sot.config.config['auth']['username'])
        self.assertEqual(CONFIG_PASSWORD,
                         sot.config.config['auth']['password'])
        self.assertEqual(CONFIG_AUTH_URL,
                         sot.config.config['auth']['auth_url'])
        self.assertEqual(CONFIG_PROJECT,
                         sot.config.config['auth']['project_name'])

    def test_from_config_given_cloud(self):
        sot = connection.from_config(cloud="sample-cloud")

        self.assertEqual(CONFIG_USERNAME,
                         sot.config.config['auth']['username'])
        self.assertEqual(CONFIG_PASSWORD,
                         sot.config.config['auth']['password'])
        self.assertEqual(CONFIG_AUTH_URL,
                         sot.config.config['auth']['auth_url'])
        self.assertEqual(CONFIG_PROJECT,
                         sot.config.config['auth']['project_name'])

    def test_from_config_given_cloud_config(self):
        cloud_region = (openstack.config.OpenStackConfig().
                        get_one("sample-cloud"))

        sot = connection.from_config(cloud_config=cloud_region)

        self.assertEqual(CONFIG_USERNAME,
                         sot.config.config['auth']['username'])
        self.assertEqual(CONFIG_PASSWORD,
                         sot.config.config['auth']['password'])
        self.assertEqual(CONFIG_AUTH_URL,
                         sot.config.config['auth']['auth_url'])
        self.assertEqual(CONFIG_PROJECT,
                         sot.config.config['auth']['project_name'])

    def test_from_config_given_cloud_name(self):
        sot = connection.from_config(cloud_name="sample-cloud")

        self.assertEqual(CONFIG_USERNAME,
                         sot.config.config['auth']['username'])
        self.assertEqual(CONFIG_PASSWORD,
                         sot.config.config['auth']['password'])
        self.assertEqual(CONFIG_AUTH_URL,
                         sot.config.config['auth']['auth_url'])
        self.assertEqual(CONFIG_PROJECT,
                         sot.config.config['auth']['project_name'])

    def test_from_config_verify(self):
        sot = connection.from_config(cloud="insecure-cloud")
        self.assertFalse(sot.session.verify)

        sot = connection.from_config(cloud="cacert-cloud")
        self.assertEqual(CONFIG_CACERT, sot.session.verify)

    def test_from_config_insecure(self):
        # Ensure that the "insecure=True" flag implies "verify=False"
        sot = connection.from_config("insecure-cloud-alternative-format")
        self.assertFalse(sot.session.verify)


class TestOsloConfig(_TestConnectionBase):
    def test_from_conf(self):
        c1 = connection.Connection(cloud='sample-cloud')
        conn = connection.Connection(
            session=c1.session, oslo_conf=self._load_ks_cfg_opts())
        # There was no config for keystone
        self.assertIsInstance(
            conn.identity, service_description._ServiceDisabledProxyShim)
        # But nova was in there
        self.assertEqual('openstack.compute.v2._proxy',
                         conn.compute.__class__.__module__)

    def test_from_conf_filter_service_types(self):
        c1 = connection.Connection(cloud='sample-cloud')
        conn = connection.Connection(
            session=c1.session, oslo_conf=self._load_ks_cfg_opts(),
            service_types={'orchestration', 'i-am-ignored'})
        # There was no config for keystone
        self.assertIsInstance(
            conn.identity, service_description._ServiceDisabledProxyShim)
        # Nova was in there, but disabled because not requested
        self.assertIsInstance(
            conn.compute, service_description._ServiceDisabledProxyShim)


class TestNetworkConnection(base.TestCase):

    # Verify that if the catalog has the suffix we don't mess things up.
    def test_network_proxy(self):
        self.os_fixture.v3_token.remove_service('network')
        svc = self.os_fixture.v3_token.add_service('network')
        svc.add_endpoint(
            interface='public',
            url='https://network.example.com/v2.0',
            region='RegionOne')
        self.use_keystone_v3()
        self.assertEqual(
            'openstack.network.v2._proxy',
            self.cloud.network.__class__.__module__)
        self.assert_calls()
        self.assertEqual(
            "https://network.example.com/v2.0",
            self.cloud.network.get_endpoint())


class TestNetworkConnectionSuffix(base.TestCase):
    # We need to do the neutron adapter test differently because it needs
    # to actually get a catalog.

    def test_network_proxy(self):
        self.assertEqual(
            'openstack.network.v2._proxy',
            self.cloud.network.__class__.__module__)
        self.assert_calls()
        self.assertEqual(
            "https://network.example.com/v2.0",
            self.cloud.network.get_endpoint())


class TestAuthorize(base.TestCase):

    def test_authorize_works(self):
        res = self.cloud.authorize()
        self.assertEqual('KeystoneToken-1', res)

    def test_authorize_failure(self):
        self.use_broken_keystone()

        self.assertRaises(openstack.exceptions.SDKException,
                          self.cloud.authorize)


class TestNewService(base.TestCase):

    def test_add_service_v1(self):
        svc = self.os_fixture.v3_token.add_service('fake')
        svc.add_endpoint(
            interface='public',
            region='RegionOne',
            url='https://fake.example.com/v1/{0}'.format(fakes.PROJECT_ID),
        )
        self.use_keystone_v3()
        conn = self.cloud

        service = fake_service.FakeService('fake')

        conn.add_service(service)

        # Ensure no discovery calls made
        self.assertEqual(0, len(self.adapter.request_history))

        self.register_uris([
            dict(method='GET',
                 uri='https://fake.example.com',
                 status_code=404),
            dict(method='GET',
                 uri='https://fake.example.com/v1/',
                 status_code=404),
            dict(method='GET',
                 uri=self.get_mock_url('fake'),
                 status_code=404),
        ])

        self.assertEqual(
            'openstack.tests.unit.fake.v1._proxy',
            conn.fake.__class__.__module__)
        self.assertTrue(conn.fake.dummy())

    def test_add_service_v2(self):
        svc = self.os_fixture.v3_token.add_service('fake')
        svc.add_endpoint(
            interface='public',
            region='RegionOne',
            url='https://fake.example.com/v2/{0}'.format(fakes.PROJECT_ID),
        )
        self.use_keystone_v3()
        conn = self.cloud

        self.register_uris([
            dict(method='GET',
                 uri='https://fake.example.com',
                 status_code=404),
            dict(method='GET',
                 uri='https://fake.example.com/v2/',
                 status_code=404),
            dict(method='GET',
                 uri=self.get_mock_url('fake'),
                 status_code=404),
        ])

        service = fake_service.FakeService('fake')

        conn.add_service(service)

        self.assertEqual(
            'openstack.tests.unit.fake.v2._proxy',
            conn.fake.__class__.__module__)
        self.assertFalse(conn.fake.dummy())

    def test_replace_system_service(self):
        svc = self.os_fixture.v3_token.add_service('fake')
        svc.add_endpoint(
            interface='public',
            region='RegionOne',
            url='https://fake.example.com/v2/{0}'.format(fakes.PROJECT_ID),
        )
        self.use_keystone_v3()
        conn = self.cloud

        # delete native dns service
        delattr(conn, 'dns')

        self.register_uris([
            dict(method='GET',
                 uri='https://fake.example.com',
                 status_code=404),
            dict(method='GET',
                 uri='https://fake.example.com/v2/',
                 status_code=404),
            dict(method='GET',
                 uri=self.get_mock_url('fake'),
                 status_code=404),
        ])

        # add fake service with alias 'DNS'
        service = fake_service.FakeService('fake', aliases=['dns'])
        conn.add_service(service)

        # ensure dns service responds as we expect from replacement
        self.assertFalse(conn.dns.dummy())


def vendor_hook(conn):
    setattr(conn, 'test', 'test_val')


class TestVendorProfile(base.TestCase):

    def setUp(self):
        super(TestVendorProfile, self).setUp()
        # Create a temporary directory where our test config will live
        # and insert it into the search path via OS_CLIENT_CONFIG_FILE.
        config_dir = self.useFixture(fixtures.TempDir()).path
        config_path = os.path.join(config_dir, "clouds.yaml")
        public_clouds = os.path.join(config_dir, "clouds-public.yaml")

        with open(config_path, "w") as conf:
            conf.write(CLOUD_CONFIG)

        with open(public_clouds, "w") as conf:
            conf.write(PUBLIC_CLOUDS_YAML)

        self.useFixture(fixtures.EnvironmentVariable(
            "OS_CLIENT_CONFIG_FILE", config_path))
        self.use_keystone_v2()

        self.config = openstack.config.loader.OpenStackConfig(
            vendor_files=[public_clouds])

    def test_conn_from_profile(self):

        self.cloud = self.config.get_one(cloud='profiled-cloud')

        conn = connection.Connection(config=self.cloud)

        self.assertIsNotNone(conn)

    def test_hook_from_profile(self):

        self.cloud = self.config.get_one(cloud='profiled-cloud')

        conn = connection.Connection(config=self.cloud)

        self.assertEqual('test_val', conn.test)

    def test_hook_from_connection_param(self):

        conn = connection.Connection(
            cloud='sample-cloud',
            vendor_hook='openstack.tests.unit.test_connection:vendor_hook'
        )

        self.assertEqual('test_val', conn.test)

    def test_hook_from_connection_ignore_missing(self):

        conn = connection.Connection(
            cloud='sample-cloud',
            vendor_hook='openstack.tests.unit.test_connection:missing'
        )

        self.assertIsNotNone(conn)
