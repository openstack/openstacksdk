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

import copy

from keystoneauth1 import exceptions as ksa_exceptions
from keystoneauth1 import session as ksa_session
import mock

from openstack import version as openstack_version
from openstack.config import cloud_region
from openstack.config import defaults
from openstack import exceptions
from openstack.tests.unit.config import base


fake_config_dict = {'a': 1, 'os_b': 2, 'c': 3, 'os_c': 4}
fake_services_dict = {
    'compute_api_version': '2',
    'compute_endpoint_override': 'http://compute.example.com',
    'telemetry_endpoint': 'http://telemetry.example.com',
    'interface': 'public',
    'image_service_type': 'mage',
    'identity_interface': 'admin',
    'identity_service_name': 'locks',
    'volume_api_version': '1',
    'auth': {'password': 'hunter2', 'username': 'AzureDiamond'},
}


class TestCloudRegion(base.TestCase):

    def test_arbitrary_attributes(self):
        cc = cloud_region.CloudRegion("test1", "region-al", fake_config_dict)
        self.assertEqual("test1", cc.name)
        self.assertEqual("region-al", cc.region_name)

        # Look up straight value
        self.assertEqual("1", cc.a)

        # Look up prefixed attribute, fail - returns None
        self.assertIsNone(cc.os_b)

        # Look up straight value, then prefixed value
        self.assertEqual("3", cc.c)
        self.assertEqual("3", cc.os_c)

        # Lookup mystery attribute
        self.assertIsNone(cc.x)

        # Test default ipv6
        self.assertFalse(cc.force_ipv4)

    def test_iteration(self):
        cc = cloud_region.CloudRegion("test1", "region-al", fake_config_dict)
        self.assertTrue('a' in cc)
        self.assertFalse('x' in cc)

    def test_equality(self):
        cc1 = cloud_region.CloudRegion("test1", "region-al", fake_config_dict)
        cc2 = cloud_region.CloudRegion("test1", "region-al", fake_config_dict)
        self.assertEqual(cc1, cc2)

    def test_inequality(self):
        cc1 = cloud_region.CloudRegion("test1", "region-al", fake_config_dict)

        cc2 = cloud_region.CloudRegion("test2", "region-al", fake_config_dict)
        self.assertNotEqual(cc1, cc2)

        cc2 = cloud_region.CloudRegion("test1", "region-xx", fake_config_dict)
        self.assertNotEqual(cc1, cc2)

        cc2 = cloud_region.CloudRegion("test1", "region-al", {})
        self.assertNotEqual(cc1, cc2)

    def test_verify(self):
        config_dict = copy.deepcopy(fake_config_dict)
        config_dict['cacert'] = None

        config_dict['verify'] = False
        cc = cloud_region.CloudRegion("test1", "region-xx", config_dict)
        (verify, cert) = cc.get_requests_verify_args()
        self.assertFalse(verify)

        config_dict['verify'] = True
        cc = cloud_region.CloudRegion("test1", "region-xx", config_dict)
        (verify, cert) = cc.get_requests_verify_args()
        self.assertTrue(verify)

    def test_verify_cacert(self):
        config_dict = copy.deepcopy(fake_config_dict)
        config_dict['cacert'] = "certfile"

        config_dict['verify'] = False
        cc = cloud_region.CloudRegion("test1", "region-xx", config_dict)
        (verify, cert) = cc.get_requests_verify_args()
        self.assertFalse(verify)

        config_dict['verify'] = True
        cc = cloud_region.CloudRegion("test1", "region-xx", config_dict)
        (verify, cert) = cc.get_requests_verify_args()
        self.assertEqual("certfile", verify)

    def test_cert_with_key(self):
        config_dict = copy.deepcopy(fake_config_dict)
        config_dict['cacert'] = None
        config_dict['verify'] = False

        config_dict['cert'] = 'cert'
        config_dict['key'] = 'key'

        cc = cloud_region.CloudRegion("test1", "region-xx", config_dict)
        (verify, cert) = cc.get_requests_verify_args()
        self.assertEqual(("cert", "key"), cert)

    def test_ipv6(self):
        cc = cloud_region.CloudRegion(
            "test1", "region-al", fake_config_dict, force_ipv4=True)
        self.assertTrue(cc.force_ipv4)

    def test_getters(self):
        cc = cloud_region.CloudRegion("test1", "region-al", fake_services_dict)

        self.assertEqual(['compute', 'identity', 'image', 'volume'],
                         sorted(cc.get_services()))
        self.assertEqual({'password': 'hunter2', 'username': 'AzureDiamond'},
                         cc.get_auth_args())
        self.assertEqual('public', cc.get_interface())
        self.assertEqual('public', cc.get_interface('compute'))
        self.assertEqual('admin', cc.get_interface('identity'))
        self.assertEqual('region-al', cc.region_name)
        self.assertIsNone(cc.get_api_version('image'))
        self.assertEqual('2', cc.get_api_version('compute'))
        self.assertEqual('mage', cc.get_service_type('image'))
        self.assertEqual('compute', cc.get_service_type('compute'))
        self.assertEqual('1', cc.get_api_version('volume'))
        self.assertEqual('volume', cc.get_service_type('volume'))
        self.assertEqual('http://compute.example.com',
                         cc.get_endpoint('compute'))
        self.assertIsNone(cc.get_endpoint('image'))
        self.assertIsNone(cc.get_service_name('compute'))
        self.assertEqual('locks', cc.get_service_name('identity'))

    def test_volume_override(self):
        cc = cloud_region.CloudRegion("test1", "region-al", fake_services_dict)
        cc.config['volume_api_version'] = '2'
        self.assertEqual('volumev2', cc.get_service_type('volume'))

    def test_volume_override_v3(self):
        cc = cloud_region.CloudRegion("test1", "region-al", fake_services_dict)
        cc.config['volume_api_version'] = '3'
        self.assertEqual('volumev3', cc.get_service_type('volume'))

    def test_workflow_override_v2(self):
        cc = cloud_region.CloudRegion("test1", "region-al", fake_services_dict)
        cc.config['workflow_api_version'] = '2'
        self.assertEqual('workflowv2', cc.get_service_type('workflow'))

    def test_no_override(self):
        """Test no override happens when defaults are not configured"""
        cc = cloud_region.CloudRegion("test1", "region-al", fake_services_dict)
        self.assertEqual('volume', cc.get_service_type('volume'))
        self.assertEqual('workflow', cc.get_service_type('workflow'))
        self.assertEqual('not-exist', cc.get_service_type('not-exist'))

    def test_get_session_no_auth(self):
        config_dict = defaults.get_defaults()
        config_dict.update(fake_services_dict)
        cc = cloud_region.CloudRegion("test1", "region-al", config_dict)
        self.assertRaises(
            exceptions.ConfigException,
            cc.get_session)

    @mock.patch.object(ksa_session, 'Session')
    def test_get_session(self, mock_session):
        config_dict = defaults.get_defaults()
        config_dict.update(fake_services_dict)
        fake_session = mock.Mock()
        fake_session.additional_user_agent = []
        mock_session.return_value = fake_session
        cc = cloud_region.CloudRegion(
            "test1", "region-al", config_dict, auth_plugin=mock.Mock())
        cc.get_session()
        mock_session.assert_called_with(
            auth=mock.ANY,
            verify=True, cert=None, timeout=None, discovery_cache=None)
        self.assertEqual(
            fake_session.additional_user_agent,
            [('openstacksdk', openstack_version.__version__)])

    @mock.patch.object(ksa_session, 'Session')
    def test_get_session_with_app_name(self, mock_session):
        config_dict = defaults.get_defaults()
        config_dict.update(fake_services_dict)
        fake_session = mock.Mock()
        fake_session.additional_user_agent = []
        fake_session.app_name = None
        fake_session.app_version = None
        mock_session.return_value = fake_session
        cc = cloud_region.CloudRegion(
            "test1", "region-al", config_dict, auth_plugin=mock.Mock(),
            app_name="test_app", app_version="test_version")
        cc.get_session()
        mock_session.assert_called_with(
            auth=mock.ANY,
            verify=True, cert=None, timeout=None, discovery_cache=None)
        self.assertEqual(fake_session.app_name, "test_app")
        self.assertEqual(fake_session.app_version, "test_version")
        self.assertEqual(
            fake_session.additional_user_agent,
            [('openstacksdk', openstack_version.__version__)])

    @mock.patch.object(ksa_session, 'Session')
    def test_get_session_with_timeout(self, mock_session):
        fake_session = mock.Mock()
        fake_session.additional_user_agent = []
        mock_session.return_value = fake_session
        config_dict = defaults.get_defaults()
        config_dict.update(fake_services_dict)
        config_dict['api_timeout'] = 9
        cc = cloud_region.CloudRegion(
            "test1", "region-al", config_dict, auth_plugin=mock.Mock())
        cc.get_session()
        mock_session.assert_called_with(
            auth=mock.ANY,
            verify=True, cert=None, timeout=9, discovery_cache=None)
        self.assertEqual(
            fake_session.additional_user_agent,
            [('openstacksdk', openstack_version.__version__)])

    @mock.patch.object(ksa_session, 'Session')
    def test_override_session_endpoint_override(self, mock_session):
        config_dict = defaults.get_defaults()
        config_dict.update(fake_services_dict)
        cc = cloud_region.CloudRegion(
            "test1", "region-al", config_dict, auth_plugin=mock.Mock())
        self.assertEqual(
            cc.get_session_endpoint('compute'),
            fake_services_dict['compute_endpoint_override'])

    @mock.patch.object(ksa_session, 'Session')
    def test_override_session_endpoint(self, mock_session):
        config_dict = defaults.get_defaults()
        config_dict.update(fake_services_dict)
        cc = cloud_region.CloudRegion(
            "test1", "region-al", config_dict, auth_plugin=mock.Mock())
        self.assertEqual(
            cc.get_session_endpoint('telemetry'),
            fake_services_dict['telemetry_endpoint'])

    @mock.patch.object(cloud_region.CloudRegion, 'get_session')
    def test_session_endpoint(self, mock_get_session):
        mock_session = mock.Mock()
        mock_get_session.return_value = mock_session
        config_dict = defaults.get_defaults()
        config_dict.update(fake_services_dict)
        cc = cloud_region.CloudRegion(
            "test1", "region-al", config_dict, auth_plugin=mock.Mock())
        cc.get_session_endpoint('orchestration')
        mock_session.get_endpoint.assert_called_with(
            interface='public',
            service_name=None,
            region_name='region-al',
            service_type='orchestration')

    @mock.patch.object(cloud_region.CloudRegion, 'get_session')
    def test_session_endpoint_not_found(self, mock_get_session):
        exc_to_raise = ksa_exceptions.catalog.EndpointNotFound
        mock_get_session.return_value.get_endpoint.side_effect = exc_to_raise
        cc = cloud_region.CloudRegion(
            "test1", "region-al", {}, auth_plugin=mock.Mock())
        self.assertIsNone(cc.get_session_endpoint('notfound'))
