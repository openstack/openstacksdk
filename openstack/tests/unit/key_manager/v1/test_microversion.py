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

from unittest import mock

from keystoneauth1.exceptions.http import NotAcceptable

from openstack.key_manager.v1 import _microversion
from openstack.tests.unit import base

ENDPOINT = 'http://localhost:9311/v1'


class TestMicroversion(base.TestCase):
    def _adapter(self, endpoint=ENDPOINT):
        adapter = mock.Mock()
        adapter.get_endpoint.return_value = endpoint
        adapter.default_microversion = None
        # mock.Mock() auto-vivifies any attribute access, which defeats the
        # getattr(..., None) "not probed yet" check in
        # _microversion.cached_microversion_range(). A real Adapter has no
        # such attribute until it's actually set, so delete the
        # auto-created one to match that behaviour.
        del adapter._key_manager_microversion_range
        return adapter

    def _response(self, json_body):
        resp = mock.Mock()
        resp.json.return_value = json_body
        return resp

    def test_probe_microversion_document(self):
        adapter = self._adapter()
        adapter.get.return_value = self._response(
            {
                'versions': [
                    {
                        'id': 'v1',
                        'status': 'CURRENT',
                        'min_version': '1.0',
                        'max_version': '1.3',
                    }
                ]
            }
        )

        min_ver, max_ver = _microversion._probe_microversion_range(adapter)

        self.assertEqual('1.0', min_ver)
        self.assertEqual('1.3', max_ver)
        adapter.get.assert_called_once_with(
            ENDPOINT,
            headers={
                'Accept': 'application/json',
                'OpenStack-API-Version': 'key-manager 1.1',
            },
            authenticated=None,
        )

    def test_probe_legacy_stable_document(self):
        # Old server: ignores the header entirely and returns the legacy
        # envelope, which has no min/max at all.
        adapter = self._adapter()
        adapter.get.return_value = self._response(
            {
                'versions': {
                    'values': [
                        {
                            'id': 'v1',
                            'status': 'stable',
                        }
                    ]
                }
            }
        )

        min_ver, max_ver = _microversion._probe_microversion_range(adapter)

        self.assertEqual('1.0', min_ver)
        self.assertEqual('1.0', max_ver)

    def test_probe_not_acceptable(self):
        adapter = self._adapter()
        adapter.get.side_effect = NotAcceptable()

        min_ver, max_ver = _microversion._probe_microversion_range(adapter)

        self.assertIsNone(min_ver)
        self.assertIsNone(max_ver)

    def test_probe_no_endpoint(self):
        adapter = self._adapter(endpoint=None)

        min_ver, max_ver = _microversion._probe_microversion_range(adapter)

        self.assertIsNone(min_ver)
        self.assertIsNone(max_ver)
        adapter.get.assert_not_called()

    def test_cached_microversion_range_probes_once(self):
        adapter = self._adapter()
        adapter.get.return_value = self._response(
            {
                'versions': [
                    {
                        'id': 'v1',
                        'status': 'CURRENT',
                        'min_version': '1.0',
                        'max_version': '1.3',
                    }
                ]
            }
        )

        first = _microversion.cached_microversion_range(adapter)
        second = _microversion.cached_microversion_range(adapter)

        self.assertEqual(('1.0', '1.3'), first)
        self.assertEqual(first, second)
        adapter.get.assert_called_once()

    def test_supports_microversion_in_range(self):
        adapter = self._adapter()
        adapter._key_manager_microversion_range = ('1.0', '1.3')

        self.assertTrue(_microversion.supports_microversion(adapter, '1.3'))
        self.assertTrue(_microversion.supports_microversion(adapter, '1.1'))

    def test_supports_microversion_out_of_range(self):
        adapter = self._adapter()
        adapter._key_manager_microversion_range = ('1.0', '1.2')

        self.assertFalse(_microversion.supports_microversion(adapter, '1.3'))

    def test_supports_microversion_no_range(self):
        adapter = self._adapter()
        adapter._key_manager_microversion_range = (None, None)

        self.assertFalse(_microversion.supports_microversion(adapter, '1.3'))

    def test_supports_microversion_respects_pinned_default(self):
        # A caller that has deliberately pinned default_microversion to
        # something lower than what the server supports has opted out of
        # the higher version, even though the server itself supports it.
        adapter = self._adapter()
        adapter._key_manager_microversion_range = ('1.0', '1.3')
        adapter.default_microversion = '1.1'

        self.assertFalse(_microversion.supports_microversion(adapter, '1.3'))
        self.assertTrue(_microversion.supports_microversion(adapter, '1.1'))

    def test_supports_microversion_pinned_default_matches(self):
        adapter = self._adapter()
        adapter._key_manager_microversion_range = ('1.0', '1.3')
        adapter.default_microversion = '1.3'

        self.assertTrue(_microversion.supports_microversion(adapter, '1.3'))

    def test_maximum_supported_microversion(self):
        adapter = self._adapter()
        adapter._key_manager_microversion_range = ('1.0', '1.3')

        self.assertEqual(
            '1.3',
            _microversion.maximum_supported_microversion(adapter, '1.3'),
        )
        self.assertEqual(
            '1.2',
            _microversion.maximum_supported_microversion(adapter, '1.2'),
        )
        self.assertIsNone(
            _microversion.maximum_supported_microversion(adapter, None)
        )

    def test_maximum_supported_microversion_no_server_range(self):
        adapter = self._adapter()
        adapter._key_manager_microversion_range = (None, None)

        self.assertIsNone(
            _microversion.maximum_supported_microversion(adapter, '1.3')
        )

    def test_maximum_supported_microversion_below_server_min(self):
        adapter = self._adapter()
        adapter._key_manager_microversion_range = ('1.2', '1.3')

        self.assertIsNone(
            _microversion.maximum_supported_microversion(adapter, '1.1')
        )

    def test_get_microversion_uses_default(self):
        adapter = self._adapter()
        adapter.default_microversion = '1.1'
        adapter._key_manager_microversion_range = ('1.0', '1.3')

        self.assertEqual('1.1', _microversion.get_microversion(adapter, '1.3'))

    def test_get_microversion_negotiates(self):
        adapter = self._adapter()
        adapter._key_manager_microversion_range = ('1.0', '1.3')

        self.assertEqual('1.3', _microversion.get_microversion(adapter, '1.3'))
