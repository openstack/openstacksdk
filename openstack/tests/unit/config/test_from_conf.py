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
            # monasca not in the service catalog
            'monasca': {},
            # Overrides for heat
            'heat': {
                'region_name': 'SpecialRegion',
                'interface': 'internal',
                'endpoint_override': 'https://example.org:8888/heat/v2'
            },
        }

    def _load_ks_cfg_opts(self):
        conf = cfg.ConfigOpts()
        for group, opts in self.oslo_config_dict.items():
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

    def test_no_adapter_opts(self):
        """Adapter opts for service type not registered."""
        del self.oslo_config_dict['heat']
        conn = self._get_conn()

        # TODO(efried): This works, even though adapter opts are not
        # registered. Should it?
        adap = conn.orchestration
        self.assertIsNone(adap.region_name)
        self.assertEqual('orchestration', adap.service_type)
        self.assertEqual('public', adap.interface)
        self.assertIsNone(adap.endpoint_override)

        self.register_uris([
            dict(method='GET',
                 uri=self.get_mock_url(
                     'orchestration', append=['foo']),
                 json={'foo': {}})
        ])
        adap.get('/foo')
        self.assert_calls()

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
