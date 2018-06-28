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

import fixtures
from keystoneauth1 import session
import mock

from openstack import connection
import openstack.config
from openstack import profile
from openstack.tests.unit import base


CONFIG_AUTH_URL = "http://127.0.0.1:5000/v2.0"
CONFIG_USERNAME = "BozoTheClown"
CONFIG_PASSWORD = "TopSecret"
CONFIG_PROJECT = "TheGrandPrizeGame"
CONFIG_CACERT = "TrustMe"

CLOUD_CONFIG = """
clouds:
  sample:
    region_name: RegionOne
    auth:
      auth_url: {auth_url}
      username: {username}
      password: {password}
      project_name: {project}
  insecure:
    auth:
      auth_url: {auth_url}
      username: {username}
      password: {password}
      project_name: {project}
    cacert: {cacert}
    verify: False
  cacert:
    auth:
      auth_url: {auth_url}
      username: {username}
      password: {password}
      project_name: {project}
    cacert: {cacert}
""".format(auth_url=CONFIG_AUTH_URL, username=CONFIG_USERNAME,
           password=CONFIG_PASSWORD, project=CONFIG_PROJECT,
           cacert=CONFIG_CACERT)


class TestConnection(base.TestCase):

    def setUp(self):
        super(TestConnection, self).setUp()
        # Create a temporary directory where our test config will live
        # and insert it into the search path via OS_CLIENT_CONFIG_FILE.
        config_dir = self.useFixture(fixtures.TempDir()).path
        config_path = os.path.join(config_dir, "clouds.yaml")

        with open(config_path, "w") as conf:
            conf.write(CLOUD_CONFIG)

        self.useFixture(fixtures.EnvironmentVariable(
            "OS_CLIENT_CONFIG_FILE", config_path))

    def test_other_parameters(self):
        conn = connection.Connection(cloud='sample', cert='cert')
        self.assertEqual(conn.session.cert, 'cert')

    def test_session_provided(self):
        mock_session = mock.Mock(spec=session.Session)
        mock_session.auth = mock.Mock()
        mock_session.auth.auth_url = 'https://auth.example.com'
        conn = connection.Connection(session=mock_session, cert='cert')
        self.assertEqual(mock_session, conn.session)
        self.assertEqual('auth.example.com', conn.config.name)

    def test_create_session(self):
        conn = connection.Connection(cloud='sample')
        self.assertEqual('openstack.proxy',
                         conn.alarm.__class__.__module__)
        self.assertEqual('openstack.clustering.v1._proxy',
                         conn.clustering.__class__.__module__)
        self.assertEqual('openstack.compute.v2._proxy',
                         conn.compute.__class__.__module__)
        self.assertEqual('openstack.database.v1._proxy',
                         conn.database.__class__.__module__)
        self.assertEqual('openstack.identity.v2._proxy',
                         conn.identity.__class__.__module__)
        self.assertEqual('openstack.image.v2._proxy',
                         conn.image.__class__.__module__)
        self.assertEqual('openstack.object_store.v1._proxy',
                         conn.object_store.__class__.__module__)
        self.assertEqual('openstack.load_balancer.v2._proxy',
                         conn.load_balancer.__class__.__module__)
        self.assertEqual('openstack.orchestration.v1._proxy',
                         conn.orchestration.__class__.__module__)
        self.assertEqual('openstack.workflow.v2._proxy',
                         conn.workflow.__class__.__module__)

    def test_create_connection_version_param_default(self):
        c1 = connection.Connection(cloud='sample')
        conn = connection.Connection(session=c1.session)
        self.assertEqual('openstack.identity.v2._proxy',
                         conn.identity.__class__.__module__)

    def test_create_connection_version_param_string(self):
        c1 = connection.Connection(cloud='sample')
        conn = connection.Connection(
            session=c1.session, identity_api_version='3')
        self.assertEqual('openstack.identity.v3._proxy',
                         conn.identity.__class__.__module__)

    def test_create_connection_version_param_int(self):
        c1 = connection.Connection(cloud='sample')
        conn = connection.Connection(
            session=c1.session, identity_api_version=3)
        self.assertEqual('openstack.identity.v3._proxy',
                         conn.identity.__class__.__module__)

    def test_create_connection_version_param_bogus(self):
        c1 = connection.Connection(cloud='sample')
        conn = connection.Connection(
            session=c1.session, identity_api_version='red')
        # TODO(mordred) This is obviously silly behavior
        self.assertEqual('openstack.identity.v3._proxy',
                         conn.identity.__class__.__module__)

    def test_from_config_given_config(self):
        cloud_region = openstack.config.OpenStackConfig().get_one("sample")

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
        sot = connection.from_config(cloud="sample")

        self.assertEqual(CONFIG_USERNAME,
                         sot.config.config['auth']['username'])
        self.assertEqual(CONFIG_PASSWORD,
                         sot.config.config['auth']['password'])
        self.assertEqual(CONFIG_AUTH_URL,
                         sot.config.config['auth']['auth_url'])
        self.assertEqual(CONFIG_PROJECT,
                         sot.config.config['auth']['project_name'])

    def test_from_config_given_cloud_config(self):
        cloud_region = openstack.config.OpenStackConfig().get_one("sample")

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
        sot = connection.from_config(cloud_name="sample")

        self.assertEqual(CONFIG_USERNAME,
                         sot.config.config['auth']['username'])
        self.assertEqual(CONFIG_PASSWORD,
                         sot.config.config['auth']['password'])
        self.assertEqual(CONFIG_AUTH_URL,
                         sot.config.config['auth']['auth_url'])
        self.assertEqual(CONFIG_PROJECT,
                         sot.config.config['auth']['project_name'])

    def test_from_config_given_options(self):
        version = "100"

        class Opts(object):
            compute_api_version = version

        sot = connection.from_config(cloud="sample", options=Opts)

        self.assertEqual(version, sot.compute.version)

    def test_from_config_verify(self):
        sot = connection.from_config(cloud="insecure")
        self.assertFalse(sot.session.verify)

        sot = connection.from_config(cloud="cacert")
        self.assertEqual(CONFIG_CACERT, sot.session.verify)

    def test_from_profile(self):
        """Copied from openstackclient/network/client.py make_client."""
        API_NAME = "network"
        instance = self.cloud_config

        prof = profile.Profile()
        prof.set_region(API_NAME, instance.region_name)
        prof.set_version(API_NAME, instance.get_api_version(API_NAME))
        prof.set_interface(API_NAME, instance.get_interface(API_NAME))
        connection.Connection(
            authenticator=instance.get_session().auth,
            verify=instance.get_session().verify,
            cert=instance.get_session().cert,
            profile=prof)


class TestNetworkConnection(base.TestCase):
    # We need to do the neutron adapter test differently because it needs
    # to actually get a catalog.

    def test_network_proxy(self):
        self.assertEqual(
            'openstack.network.v2._proxy',
            self.conn.network.__class__.__module__)
        self.assert_calls()
        self.assertEqual(
            "https://network.example.com/v2.0",
            self.conn.network.get_endpoint())


class TestAuthorize(base.TestCase):

    def test_authorize_works(self):
        res = self.conn.authorize()
        self.assertEqual('KeystoneToken-1', res)

    def test_authorize_failure(self):
        self.use_broken_keystone()

        self.assertRaises(openstack.exceptions.HttpException,
                          self.conn.authorize)
