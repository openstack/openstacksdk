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

from keystoneauth1 import exceptions as ks_exc
from keystoneauth1 import loading as ks_loading
from oslo_config import cfg

from openstack.config import cloud_region
from openstack import connection
from openstack import exceptions
from openstack.tests import fakes
from openstack.tests.unit import base


class TestFromConf(base.TestCase):

    def setUp(self):
        super(TestFromConf, self).setUp()
        self.oslo_config_dict = {
            # All defaults for nova
            'nova': {},
            # monasca-api not in the service catalog
            'monasca-api': {},
            # Overrides for heat
            'heat': {
                'region_name': 'SpecialRegion',
                'interface': 'internal',
                'endpoint_override': 'https://example.org:8888/heat/v2'
            },
            # test a service with dashes
            'ironic_inspector': {
                'endpoint_override': 'https://example.org:5050',
            },
        }

    def _load_ks_cfg_opts(self):
        conf = cfg.ConfigOpts()
        for group, opts in self.oslo_config_dict.items():
            conf.register_group(cfg.OptGroup(group))
            if opts is not None:
                ks_loading.register_adapter_conf_options(conf, group)
                for name, val in opts.items():
                    conf.set_override(name, val, group=group)
        return conf

    def _get_conn(self):
        oslocfg = self._load_ks_cfg_opts()
        # Throw name in here to prove **kwargs is working
        config = cloud_region.from_conf(
            oslocfg, session=self.cloud.session, name='from_conf.example.com')
        self.assertEqual('from_conf.example.com', config.name)

        return connection.Connection(config=config)

    def test_adapter_opts_set(self):
        """Adapter opts specified in the conf."""
        conn = self._get_conn()

        discovery = {
            "versions": {
                "values": [
                    {"status": "stable",
                     "updated": "2019-06-01T00:00:00Z",
                     "media-types": [{
                         "base": "application/json",
                         "type": "application/vnd.openstack.heat-v2+json"}],
                     "id": "v2.0",
                     "links": [{
                         "href": "https://example.org:8888/heat/v2",
                         "rel": "self"}]
                     }]
            }
        }
        self.register_uris([
            dict(method='GET',
                 uri='https://example.org:8888/heat/v2',
                 json=discovery),
            dict(method='GET',
                 uri='https://example.org:8888/heat/v2/foo',
                 json={'foo': {}}),
        ])

        adap = conn.orchestration
        self.assertEqual('SpecialRegion', adap.region_name)
        self.assertEqual('orchestration', adap.service_type)
        self.assertEqual('internal', adap.interface)
        self.assertEqual('https://example.org:8888/heat/v2',
                         adap.endpoint_override)

        adap.get('/foo')
        self.assert_calls()

    def test_default_adapter_opts(self):
        """Adapter opts are registered, but all defaulting in conf."""
        conn = self._get_conn()

        # Nova has empty adapter config, so these default
        adap = conn.compute
        self.assertIsNone(adap.region_name)
        self.assertEqual('compute', adap.service_type)
        self.assertEqual('public', adap.interface)
        self.assertIsNone(adap.endpoint_override)

        server_id = str(uuid.uuid4())
        server_name = self.getUniqueString('name')
        fake_server = fakes.make_fake_server(server_id, server_name)
        self.register_uris([
            self.get_nova_discovery_mock_dict(),
            dict(method='GET',
                 uri=self.get_mock_url(
                     'compute', 'public', append=['servers', 'detail']),
                 json={'servers': [fake_server]}),
        ])
        s = next(adap.servers())
        self.assertEqual(s.id, server_id)
        self.assertEqual(s.name, server_name)
        self.assert_calls()

    def test_name_with_dashes(self):
        conn = self._get_conn()

        discovery = {
            "versions": {
                "values": [
                    {"status": "stable",
                     "id": "v1",
                     "links": [{
                         "href": "https://example.org:5050/v1",
                         "rel": "self"}]
                     }]
            }
        }
        status = {
            'finished': True,
            'error': None
        }
        self.register_uris([
            dict(method='GET',
                 uri='https://example.org:5050',
                 json=discovery),
            dict(method='GET',
                 uri='https://example.org:5050/v1/introspection/abcd',
                 json=status),
        ])

        adap = conn.baremetal_introspection
        self.assertEqual('baremetal-introspection', adap.service_type)
        self.assertEqual('public', adap.interface)
        self.assertEqual('https://example.org:5050/v1', adap.endpoint_override)

        self.assertTrue(adap.get_introspection('abcd').is_finished)

    def _test_missing_invalid_permutations(self, expected_reason):
        # Do special things to self.oslo_config_dict['heat'] before calling
        # this method.
        conn = self._get_conn()

        adap = conn.orchestration
        ex = self.assertRaises(
            exceptions.ServiceDisabledException, getattr, adap, 'get')
        self.assertIn("Service 'orchestration' is disabled because its "
                      "configuration could not be loaded.", ex.message)
        self.assertIn(expected_reason, ex.message)

    def test_no_such_conf_section(self):
        """No conf section (therefore no adapter opts) for service type."""
        del self.oslo_config_dict['heat']
        self._test_missing_invalid_permutations(
            "No section for project 'heat' (service type 'orchestration') was "
            "present in the config.")

    def test_no_adapter_opts(self):
        """Conf section present, but opts for service type not registered."""
        self.oslo_config_dict['heat'] = None
        self._test_missing_invalid_permutations(
            "Encountered an exception attempting to process config for "
            "project 'heat' (service type 'orchestration'): no such option")

    def test_invalid_adapter_opts(self):
        """Adapter opts are bogus, in exception-raising ways."""
        self.oslo_config_dict['heat'] = {
            'interface': 'public',
            'valid_interfaces': 'private',
        }
        self._test_missing_invalid_permutations(
            "Encountered an exception attempting to process config for "
            "project 'heat' (service type 'orchestration'): interface and "
            "valid_interfaces are mutually exclusive.")

    def test_no_session(self):
        # TODO(efried): Currently calling without a Session is not implemented.
        self.assertRaises(exceptions.ConfigException,
                          cloud_region.from_conf, self._load_ks_cfg_opts())

    def test_no_endpoint(self):
        """Conf contains adapter opts, but service type not in catalog."""
        conn = self._get_conn()
        # Monasca is not in the service catalog
        self.assertRaises(ks_exc.catalog.EndpointNotFound,
                          getattr, conn, 'monitoring')
