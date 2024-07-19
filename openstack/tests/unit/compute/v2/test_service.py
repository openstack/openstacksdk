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

from openstack.compute.v2 import service
from openstack import exceptions
from openstack.tests.unit import base

IDENTIFIER = 'IDENTIFIER'
EXAMPLE = {
    'id': IDENTIFIER,
    'binary': 'nova-compute',
    'host': 'host1',
    'status': 'enabled',
    'state': 'up',
    'zone': 'nova',
}


class TestService(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = {'service': {}}
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.status_code = 200
        self.resp.headers = {}
        self.sess = mock.Mock()
        self.sess.put = mock.Mock(return_value=self.resp)
        self.sess.default_microversion = '2.1'

    def test_basic(self):
        sot = service.Service()
        self.assertEqual('service', sot.resource_key)
        self.assertEqual('services', sot.resources_key)
        self.assertEqual('/os-services', sot.base_path)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_list)
        self.assertFalse(sot.allow_fetch)

        self.assertDictEqual(
            {
                'binary': 'binary',
                'host': 'host',
                'limit': 'limit',
                'marker': 'marker',
                'name': 'binary',
            },
            sot._query_mapping._mapping,
        )

    def test_make_it(self):
        sot = service.Service(**EXAMPLE)
        self.assertEqual(EXAMPLE['host'], sot.host)
        self.assertEqual(EXAMPLE['binary'], sot.binary)
        self.assertEqual(EXAMPLE['binary'], sot.name)
        self.assertEqual(EXAMPLE['status'], sot.status)
        self.assertEqual(EXAMPLE['state'], sot.state)
        self.assertEqual(EXAMPLE['zone'], sot.availability_zone)
        self.assertEqual(EXAMPLE['id'], sot.id)

    def test_find_single_match(self):
        data = [
            service.Service(name='bin1', host='host', id=1),
            service.Service(name='bin2', host='host', id=2),
        ]
        with mock.patch.object(service.Service, 'list') as list_mock:
            list_mock.return_value = data

            sot = service.Service.find(
                self.sess, 'bin1', ignore_missing=True, host='host'
            )

            self.assertEqual(data[0], sot)

    def test_find_with_id_single_match(self):
        data = [
            service.Service(name='bin1', host='host', id=1),
            service.Service(name='bin2', host='host', id='2'),
        ]
        with mock.patch.object(service.Service, 'list') as list_mock:
            list_mock.return_value = data

            sot = service.Service.find(
                self.sess, '2', ignore_missing=True, binary='bin1', host='host'
            )

            self.assertEqual(data[1], sot)

            # Verify find when ID is int
            sot = service.Service.find(
                self.sess, 1, ignore_missing=True, binary='bin1', host='host'
            )

            self.assertEqual(data[0], sot)

    def test_find_no_match(self):
        data = [
            service.Service(name='bin1', host='host', id=1),
            service.Service(name='bin2', host='host', id=2),
        ]
        with mock.patch.object(service.Service, 'list') as list_mock:
            list_mock.return_value = data

            self.assertIsNone(
                service.Service.find(
                    self.sess, 'fake', ignore_missing=True, host='host'
                )
            )

    def test_find_no_match_exception(self):
        data = [
            service.Service(name='bin1', host='host', id=1),
            service.Service(name='bin2', host='host', id=2),
        ]
        with mock.patch.object(service.Service, 'list') as list_mock:
            list_mock.return_value = data

            self.assertRaises(
                exceptions.NotFoundException,
                service.Service.find,
                self.sess,
                'fake',
                ignore_missing=False,
                host='host',
            )

    def test_find_multiple_match(self):
        data = [
            service.Service(name='bin1', host='host', id=1),
            service.Service(name='bin1', host='host', id=2),
        ]
        with mock.patch.object(service.Service, 'list') as list_mock:
            list_mock.return_value = data

            self.assertRaises(
                exceptions.DuplicateResource,
                service.Service.find,
                self.sess,
                'bin1',
                ignore_missing=False,
                host='host',
            )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=False,
    )
    def test_set_forced_down_before_211(self, mv_mock):
        sot = service.Service(**EXAMPLE)

        res = sot.set_forced_down(self.sess, 'host1', 'nova-compute', True)
        self.assertIsNotNone(res)

        url = 'os-services/force-down'
        body = {
            'binary': 'nova-compute',
            'host': 'host1',
        }
        self.sess.put.assert_called_with(
            url, json=body, microversion=self.sess.default_microversion
        )

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=True,
    )
    def test_set_forced_down_after_211(self, mv_mock):
        sot = service.Service(**EXAMPLE)

        res = sot.set_forced_down(self.sess, 'host1', 'nova-compute', True)
        self.assertIsNotNone(res)

        url = 'os-services/force-down'
        body = {
            'binary': 'nova-compute',
            'host': 'host1',
            'forced_down': True,
        }
        self.sess.put.assert_called_with(url, json=body, microversion='2.11')

    @mock.patch(
        'openstack.utils.supports_microversion',
        autospec=True,
        return_value=True,
    )
    def test_set_forced_down_after_253(self, mv_mock):
        sot = service.Service(**EXAMPLE)

        res = sot.set_forced_down(self.sess, None, None, True)
        self.assertIsNotNone(res)

        url = 'os-services/force-down'
        body = {
            'binary': sot.binary,
            'host': sot.host,
            'forced_down': True,
        }
        self.sess.put.assert_called_with(url, json=body, microversion='2.11')

    def test_enable(self):
        sot = service.Service(**EXAMPLE)

        res = sot.enable(self.sess, 'host1', 'nova-compute')
        self.assertIsNotNone(res)

        url = 'os-services/enable'
        body = {
            'binary': 'nova-compute',
            'host': 'host1',
        }
        self.sess.put.assert_called_with(
            url, json=body, microversion=self.sess.default_microversion
        )

    def test_disable(self):
        sot = service.Service(**EXAMPLE)

        res = sot.disable(self.sess, 'host1', 'nova-compute')
        self.assertIsNotNone(res)

        url = 'os-services/disable'
        body = {
            'binary': 'nova-compute',
            'host': 'host1',
        }
        self.sess.put.assert_called_with(
            url, json=body, microversion=self.sess.default_microversion
        )

    def test_disable_with_reason(self):
        sot = service.Service(**EXAMPLE)
        reason = 'fencing'

        res = sot.disable(self.sess, 'host1', 'nova-compute', reason=reason)

        self.assertIsNotNone(res)

        url = 'os-services/disable-log-reason'
        body = {
            'binary': 'nova-compute',
            'host': 'host1',
            'disabled_reason': reason,
        }
        self.sess.put.assert_called_with(
            url, json=body, microversion=self.sess.default_microversion
        )
