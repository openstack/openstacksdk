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

from openstack.auth.identity import v2
from openstack import connection
from openstack import profile
from openstack.tests.unit import base
from openstack import transport


CONFIG_AUTH_URL = "http://127.0.0.1:5000/v2.0"
CONFIG_USERNAME = "BozoTheClown"
CONFIG_PASSWORD = "TopSecret"
CONFIG_PROJECT = "TheGrandPrizeGame"

CLOUD_CONFIG = """
clouds:
  sample:
    region_name: RegionOne
    auth:
      auth_url: {auth_url}
      username: {username}
      password: {password}
      project_name: {project}
""".format(auth_url=CONFIG_AUTH_URL, username=CONFIG_USERNAME,
           password=CONFIG_PASSWORD, project=CONFIG_PROJECT)


class TestConnection(base.TestCase):
    def setUp(self):
        super(TestConnection, self).setUp()
        self.xport = transport.Transport()
        self.auth = v2.Token(auth_url='http://127.0.0.1/v2', token='b')
        self.prof = profile.Profile()
        self.conn = connection.Connection(authenticator=mock.MagicMock(),
                                          transport=mock.MagicMock())
        self.conn.session = mock.MagicMock()

    def test_create_transport(self):
        conn = connection.Connection(authenticator='2', verify=True,
                                     user_agent='1')
        self.assertTrue(conn.transport.verify)
        self.assertIn('1', conn.transport._user_agent)

    def test_create_authenticator(self):
        auth_args = {
            'auth_url': '0',
            'username': '1',
            'password': '2',
        }
        conn = connection.Connection(transport='0', auth_plugin='password',
                                     **auth_args)
        self.assertEqual('0', conn.authenticator.auth_url)
        self.assertEqual(
            '1',
            conn.authenticator.auth_plugin.auth_methods[0].username)
        self.assertEqual(
            '2',
            conn.authenticator.auth_plugin.auth_methods[0].password)

    def test_create_session(self):
        args = {
            'transport': self.xport,
            'authenticator': self.auth,
            'profile': self.prof,
        }
        conn = connection.Connection(**args)
        self.assertEqual(self.xport, conn.session.transport)
        self.assertEqual(self.auth, conn.session.authenticator)
        self.assertEqual(self.prof, conn.session.profile)
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

    def test_custom_user_agent(self):
        user_agent = "MyProgram/1.0"
        conn = connection.Connection(authenticator=self.auth,
                                     user_agent=user_agent)
        self.assertTrue(conn.transport._user_agent.startswith(user_agent))

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
                         sot.authenticator.auth_plugin.username)
        self.assertEqual(CONFIG_PASSWORD,
                         sot.authenticator.auth_plugin.password)
        self.assertEqual(CONFIG_AUTH_URL,
                         sot.authenticator.auth_plugin.auth_url)
        self.assertEqual(CONFIG_PROJECT,
                         sot.authenticator.auth_plugin.tenant_name)

    def test_from_config_given_name(self):
        self._prepare_test_config()

        sot = connection.from_config(cloud_name="sample")

        self.assertEqual(CONFIG_USERNAME,
                         sot.authenticator.auth_plugin.username)
        self.assertEqual(CONFIG_PASSWORD,
                         sot.authenticator.auth_plugin.password)
        self.assertEqual(CONFIG_AUTH_URL,
                         sot.authenticator.auth_plugin.auth_url)
        self.assertEqual(CONFIG_PROJECT,
                         sot.authenticator.auth_plugin.tenant_name)

    def test_from_config_given_options(self):
        self._prepare_test_config()

        version = "100"

        class Opts(object):
            compute_api_version = version

        sot = connection.from_config(cloud_name="sample", options=Opts)

        pref = sot.session.profile.get_preference("compute")

        # NOTE: Along the way, the `v` prefix gets added so we can build
        # up URLs with it.
        self.assertEqual("v" + version, pref.version)
