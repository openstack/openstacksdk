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
import tempfile

import mock
import os_client_config

from openstack import connection
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
    insecure: True
  cacert:
    auth:
      auth_url: {auth_url}
      username: {username}
      password: {password}
      project_name: {project}
    cacert: {cacert}
    insecure: False
""".format(auth_url=CONFIG_AUTH_URL, username=CONFIG_USERNAME,
           password=CONFIG_PASSWORD, project=CONFIG_PROJECT,
           cacert=CONFIG_CACERT)


class TestConnection(base.TestCase):
    @mock.patch("openstack.session.Session")
    def test_other_parameters(self, mock_session_init):
        mock_session_init.return_value = mock_session_init
        mock_profile = mock.Mock()
        mock_profile.get_services = mock.Mock(return_value=[])
        conn = connection.Connection(profile=mock_profile, authenticator='2',
                                     verify=True, cert='cert', user_agent='1')
        args = {'auth': '2', 'user_agent': '1', 'verify': True, 'cert': 'cert'}
        mock_session_init.assert_called_with(mock_profile, **args)
        self.assertEqual(mock_session_init, conn.session)

    @mock.patch("keystoneauth1.loading.base.get_plugin_loader")
    def test_create_authenticator(self, mock_get_plugin):
        mock_plugin = mock.Mock()
        mock_loader = mock.Mock()
        mock_options = [
            mock.Mock(dest="auth_url"),
            mock.Mock(dest="password"),
            mock.Mock(dest="username"),
        ]
        mock_loader.get_options = mock.Mock(return_value=mock_options)
        mock_loader.load_from_options = mock.Mock(return_value=mock_plugin)
        mock_get_plugin.return_value = mock_loader
        auth_args = {
            'auth_url': '0',
            'username': '1',
            'password': '2',
        }
        conn = connection.Connection(auth_plugin='v2password', **auth_args)
        mock_get_plugin.assert_called_with('v2password')
        mock_loader.load_from_options.assert_called_with(**auth_args)
        self.assertEqual(mock_plugin, conn.authenticator)

    @mock.patch("keystoneauth1.loading.base.get_plugin_loader")
    def test_default_plugin(self, mock_get_plugin):
        connection.Connection()
        self.assertTrue(mock_get_plugin.called)
        self.assertEqual(mock_get_plugin.call_args, mock.call("password"))

    @mock.patch("keystoneauth1.loading.base.get_plugin_loader")
    def test_pass_authenticator(self, mock_get_plugin):
        mock_plugin = mock.Mock()
        mock_get_plugin.return_value = None
        conn = connection.Connection(authenticator=mock_plugin)
        self.assertFalse(mock_get_plugin.called)
        self.assertEqual(mock_plugin, conn.authenticator)

    def test_create_session(self):
        auth = mock.Mock()
        prof = profile.Profile()
        conn = connection.Connection(authenticator=auth, profile=prof)
        self.assertEqual(auth, conn.authenticator)
        self.assertEqual(prof, conn.profile)
        self.assertEqual('openstack.cluster.v1._proxy',
                         conn.cluster.__class__.__module__)
        self.assertEqual('openstack.compute.v2._proxy',
                         conn.compute.__class__.__module__)
        self.assertEqual('openstack.database.v1._proxy',
                         conn.database.__class__.__module__)
        self.assertEqual('openstack.identity.v3._proxy',
                         conn.identity.__class__.__module__)
        self.assertEqual('openstack.image.v1._proxy',
                         conn.image.__class__.__module__)
        self.assertEqual('openstack.network.v2._proxy',
                         conn.network.__class__.__module__)
        self.assertEqual('openstack.object_store.v1._proxy',
                         conn.object_store.__class__.__module__)
        self.assertEqual('openstack.orchestration.v1._proxy',
                         conn.orchestration.__class__.__module__)
        self.assertEqual('openstack.telemetry.v2._proxy',
                         conn.telemetry.__class__.__module__)

    def _prepare_test_config(self):
        # Create a temporary directory where our test config will live
        # and insert it into the search path via OS_CLIENT_CONFIG_FILE.
        # NOTE: If OCC stops popping OS_C_C_F off of os.environ, this
        # will need to change to respect that. It currently works between
        # tests because the environment variable is always wiped by OCC itself.
        config_dir = tempfile.mkdtemp()
        config_path = os.path.join(config_dir, "clouds.yaml")

        with open(config_path, "w") as conf:
            conf.write(CLOUD_CONFIG)

        os.environ["OS_CLIENT_CONFIG_FILE"] = config_path

    def test_from_config_given_data(self):
        self._prepare_test_config()

        data = os_client_config.OpenStackConfig().get_one_cloud("sample")

        sot = connection.from_config(cloud_config=data)

        self.assertEqual(CONFIG_USERNAME,
                         sot.authenticator._username)
        self.assertEqual(CONFIG_PASSWORD,
                         sot.authenticator._password)
        self.assertEqual(CONFIG_AUTH_URL,
                         sot.authenticator.auth_url)
        self.assertEqual(CONFIG_PROJECT,
                         sot.authenticator._project_name)

    def test_from_config_given_name(self):
        self._prepare_test_config()

        sot = connection.from_config(cloud_name="sample")

        self.assertEqual(CONFIG_USERNAME,
                         sot.authenticator._username)
        self.assertEqual(CONFIG_PASSWORD,
                         sot.authenticator._password)
        self.assertEqual(CONFIG_AUTH_URL,
                         sot.authenticator.auth_url)
        self.assertEqual(CONFIG_PROJECT,
                         sot.authenticator._project_name)

    def test_from_config_given_options(self):
        self._prepare_test_config()

        version = "100"

        class Opts(object):
            compute_api_version = version

        sot = connection.from_config(cloud_name="sample", options=Opts)

        pref = sot.session.profile.get_filter("compute")

        # NOTE: Along the way, the `v` prefix gets added so we can build
        # up URLs with it.
        self.assertEqual("v" + version, pref.version)

    def test_from_config_verify(self):
        self._prepare_test_config()

        sot = connection.from_config(cloud_name="insecure")
        self.assertFalse(sot.session.verify)

        sot = connection.from_config(cloud_name="cacert")
        self.assertEqual(CONFIG_CACERT, sot.session.verify)

    def test_authorize_works(self):
        fake_session = mock.Mock()
        fake_headers = {'X-Auth-Token': 'FAKE_TOKEN'}
        fake_session.get_auth_headers.return_value = fake_headers

        sot = connection.Connection(session=fake_session,
                                    authenticator=mock.Mock())
        res = sot.authorize()
        self.assertEqual('FAKE_TOKEN', res)

    def test_authorize_silent_failure(self):
        fake_session = mock.Mock()
        fake_session.get_auth_headers.return_value = None

        sot = connection.Connection(session=fake_session,
                                    authenticator=mock.Mock())
        res = sot.authorize()
        self.assertIsNone(res)
