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
from unittest import mock

from keystoneauth1 import exceptions as ksa_exceptions
from keystoneauth1 import session as ksa_session

from openstack.config import cloud_region
from openstack.config import defaults
from openstack import exceptions
from openstack.tests.unit.config import base
from openstack import version as openstack_version

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
    'connect_retries': 1,
    'baremetal_status_code_retries': 5,
    'baremetal_connect_retries': 3,
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

    def test_get_config(self):
        cc = cloud_region.CloudRegion("test1", "region-al", fake_services_dict)
        self.assertIsNone(cc._get_config('nothing', None))
        # This is what is happening behind the scenes in get_default_interface.
        self.assertEqual(
            fake_services_dict['interface'],
            cc._get_config('interface', None))
        # The same call as above, but from one step up the stack
        self.assertEqual(
            fake_services_dict['interface'],
            cc.get_interface())
        # Which finally is what is called to populate the below
        self.assertEqual('public', self.cloud.default_interface)

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

        config_dict['insecure'] = True
        cc = cloud_region.CloudRegion("test1", "region-xx", config_dict)
        (verify, cert) = cc.get_requests_verify_args()
        self.assertFalse(verify)

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

        config_dict['insecure'] = True
        cc = cloud_region.CloudRegion("test1", "region-xx", config_dict)
        (verify, cert) = cc.get_requests_verify_args()
        self.assertEqual(False, verify)

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
        self.assertEqual('block-storage', cc.get_service_type('volume'))
        self.assertEqual('http://compute.example.com',
                         cc.get_endpoint('compute'))
        self.assertIsNone(cc.get_endpoint('image'))
        self.assertIsNone(cc.get_service_name('compute'))
        self.assertEqual('locks', cc.get_service_name('identity'))
        self.assertIsNone(cc.get_status_code_retries('compute'))
        self.assertEqual(5, cc.get_status_code_retries('baremetal'))
        self.assertEqual(1, cc.get_connect_retries('compute'))
        self.assertEqual(3, cc.get_connect_retries('baremetal'))

    def test_rackspace_workaround(self):
        # We're skipping loader here, so we have to expand relevant
        # parts from the rackspace profile. The thing we're testing
        # is that the project_id logic works.
        cc = cloud_region.CloudRegion("test1", "DFW", {
            'profile': 'rackspace',
            'region_name': 'DFW',
            'auth': {'project_id': '123456'},
            'block_storage_endpoint_override': 'https://example.com/v2/',
        })
        self.assertEqual(
            'https://example.com/v2/123456',
            cc.get_endpoint('block-storage')
        )

    def test_rackspace_workaround_only_rax(self):
        cc = cloud_region.CloudRegion("test1", "DFW", {
            'region_name': 'DFW',
            'auth': {'project_id': '123456'},
            'block_storage_endpoint_override': 'https://example.com/v2/',
        })
        self.assertEqual(
            'https://example.com/v2/',
            cc.get_endpoint('block-storage')
        )

    def test_get_region_name(self):

        def assert_region_name(default, compute):
            self.assertEqual(default, cc.region_name)
            self.assertEqual(default, cc.get_region_name())
            self.assertEqual(default, cc.get_region_name(service_type=None))
            self.assertEqual(
                compute, cc.get_region_name(service_type='compute'))
            self.assertEqual(
                default, cc.get_region_name(service_type='placement'))

        # No region_name kwarg, no regions specified in services dict
        # (including the default).
        cc = cloud_region.CloudRegion(config=fake_services_dict)
        assert_region_name(None, None)

        # Only region_name kwarg; it's returned for everything
        cc = cloud_region.CloudRegion(
            region_name='foo', config=fake_services_dict)
        assert_region_name('foo', 'foo')

        # No region_name kwarg; values (including default) show through from
        # config dict
        services_dict = dict(
            fake_services_dict,
            region_name='the-default', compute_region_name='compute-region')
        cc = cloud_region.CloudRegion(config=services_dict)
        assert_region_name('the-default', 'compute-region')

        # region_name kwarg overrides config dict default (for backward
        # compatibility), but service-specific region_name takes precedence.
        services_dict = dict(
            fake_services_dict,
            region_name='dict', compute_region_name='compute-region')
        cc = cloud_region.CloudRegion(
            region_name='kwarg', config=services_dict)
        assert_region_name('kwarg', 'compute-region')

    def test_aliases(self):
        services_dict = fake_services_dict.copy()
        services_dict['volume_api_version'] = 12
        services_dict['alarming_service_name'] = 'aodh'
        cc = cloud_region.CloudRegion("test1", "region-al", services_dict)
        self.assertEqual('12', cc.get_api_version('volume'))
        self.assertEqual('12', cc.get_api_version('block-storage'))
        self.assertEqual('aodh', cc.get_service_name('alarm'))
        self.assertEqual('aodh', cc.get_service_name('alarming'))

    def test_no_override(self):
        """Test no override happens when defaults are not configured"""
        cc = cloud_region.CloudRegion("test1", "region-al", fake_services_dict)
        self.assertEqual('block-storage', cc.get_service_type('volume'))
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
            verify=True, cert=None, timeout=None, collect_timing=None,
            discovery_cache=None)
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
            verify=True, cert=None, timeout=None, collect_timing=None,
            discovery_cache=None)
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
            verify=True, cert=None, timeout=9,
            collect_timing=None, discovery_cache=None)
        self.assertEqual(
            fake_session.additional_user_agent,
            [('openstacksdk', openstack_version.__version__)])

    @mock.patch.object(ksa_session, 'Session')
    def test_get_session_with_timing(self, mock_session):
        fake_session = mock.Mock()
        fake_session.additional_user_agent = []
        mock_session.return_value = fake_session
        config_dict = defaults.get_defaults()
        config_dict.update(fake_services_dict)
        config_dict['timing'] = True
        cc = cloud_region.CloudRegion(
            "test1", "region-al", config_dict, auth_plugin=mock.Mock())
        cc.get_session()
        mock_session.assert_called_with(
            auth=mock.ANY,
            verify=True, cert=None, timeout=None,
            collect_timing=True, discovery_cache=None)
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

    def test_get_endpoint_from_catalog(self):
        dns_override = 'https://override.dns.example.com'
        self.cloud.config.config['dns_endpoint_override'] = dns_override
        self.assertEqual(
            'https://compute.example.com/v2.1/',
            self.cloud.config.get_endpoint_from_catalog('compute'))
        self.assertEqual(
            'https://internal.compute.example.com/v2.1/',
            self.cloud.config.get_endpoint_from_catalog(
                'compute', interface='internal'))
        self.assertIsNone(
            self.cloud.config.get_endpoint_from_catalog(
                'compute', region_name='unknown-region'))
        self.assertEqual(
            'https://dns.example.com',
            self.cloud.config.get_endpoint_from_catalog('dns'))
