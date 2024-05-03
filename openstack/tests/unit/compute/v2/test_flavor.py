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

from keystoneauth1 import adapter

from openstack.compute.v2 import flavor
from openstack.tests.unit import base


IDENTIFIER = 'IDENTIFIER'
BASIC_EXAMPLE = {
    'id': IDENTIFIER,
    'links': '2',
    'name': '3',
    'description': 'Testing flavor',
    'disk': 4,
    'os-flavor-access:is_public': True,
    'ram': 6,
    'vcpus': 7,
    'swap': 8,
    'OS-FLV-EXT-DATA:ephemeral': 9,
    'OS-FLV-DISABLED:disabled': False,
    'rxtx_factor': 11.0,
}
DEFAULTS_EXAMPLE = {
    'links': '2',
    'original_name': IDENTIFIER,
    'description': 'Testing flavor',
}


class TestFlavor(base.TestCase):
    def setUp(self):
        super().setUp()
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.default_microversion = 1
        self.sess._get_connection = mock.Mock(return_value=self.cloud)

    def test_basic(self):
        sot = flavor.Flavor()
        self.assertEqual('flavor', sot.resource_key)
        self.assertEqual('flavors', sot.resources_key)
        self.assertEqual('/flavors', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)
        self.assertTrue(sot.allow_commit)

        self.assertDictEqual(
            {
                "sort_key": "sort_key",
                "sort_dir": "sort_dir",
                "min_disk": "minDisk",
                "min_ram": "minRam",
                "limit": "limit",
                "marker": "marker",
                "is_public": "is_public",
            },
            sot._query_mapping._mapping,
        )

    def test_make_basic(self):
        sot = flavor.Flavor(**BASIC_EXAMPLE)
        self.assertEqual(BASIC_EXAMPLE['id'], sot.id)
        self.assertEqual(BASIC_EXAMPLE['name'], sot.name)
        self.assertEqual(BASIC_EXAMPLE['description'], sot.description)
        self.assertEqual(BASIC_EXAMPLE['disk'], sot.disk)
        self.assertEqual(
            BASIC_EXAMPLE['os-flavor-access:is_public'], sot.is_public
        )
        self.assertEqual(BASIC_EXAMPLE['ram'], sot.ram)
        self.assertEqual(BASIC_EXAMPLE['vcpus'], sot.vcpus)
        self.assertEqual(BASIC_EXAMPLE['swap'], sot.swap)
        self.assertEqual(
            BASIC_EXAMPLE['OS-FLV-EXT-DATA:ephemeral'], sot.ephemeral
        )
        self.assertEqual(
            BASIC_EXAMPLE['OS-FLV-DISABLED:disabled'], sot.is_disabled
        )
        self.assertEqual(BASIC_EXAMPLE['rxtx_factor'], sot.rxtx_factor)

    def test_make_basic_swap(self):
        sot = flavor.Flavor(id=IDENTIFIER, swap="")
        self.assertEqual(0, sot.swap)
        sot1 = flavor.Flavor(id=IDENTIFIER, swap=0)
        self.assertEqual(0, sot1.swap)

    def test_make_defaults(self):
        sot = flavor.Flavor(**DEFAULTS_EXAMPLE)
        self.assertEqual(DEFAULTS_EXAMPLE['original_name'], sot.name)
        self.assertEqual(0, sot.disk)
        self.assertEqual(True, sot.is_public)
        self.assertEqual(0, sot.ram)
        self.assertEqual(0, sot.vcpus)
        self.assertEqual(0, sot.swap)
        self.assertEqual(0, sot.ephemeral)
        self.assertEqual(IDENTIFIER, sot.id)

    def test_flavor_id(self):
        id = 'fake_id'
        sot = flavor.Flavor(id=id)
        self.assertEqual(sot.id, id)
        sot = flavor.Flavor(name=id)
        self.assertEqual(sot.id, id)
        self.assertEqual(sot.name, id)
        sot = flavor.Flavor(original_name=id)
        self.assertEqual(sot.id, id)
        self.assertEqual(sot.original_name, id)

    def test_add_tenant_access(self):
        sot = flavor.Flavor(**BASIC_EXAMPLE)
        resp = mock.Mock()
        resp.body = None
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.post = mock.Mock(return_value=resp)

        sot.add_tenant_access(self.sess, 'fake_tenant')

        self.sess.post.assert_called_with(
            'flavors/IDENTIFIER/action',
            json={'addTenantAccess': {'tenant': 'fake_tenant'}},
            headers={'Accept': ''},
        )

    def test_remove_tenant_access(self):
        sot = flavor.Flavor(**BASIC_EXAMPLE)
        resp = mock.Mock()
        resp.body = None
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.post = mock.Mock(return_value=resp)

        sot.remove_tenant_access(self.sess, 'fake_tenant')

        self.sess.post.assert_called_with(
            'flavors/IDENTIFIER/action',
            json={'removeTenantAccess': {'tenant': 'fake_tenant'}},
            headers={'Accept': ''},
        )

    def test_get_flavor_access(self):
        sot = flavor.Flavor(**BASIC_EXAMPLE)
        resp = mock.Mock()
        resp.body = {
            'flavor_access': [
                {'flavor_id': 'fake_flavor', 'tenant_id': 'fake_tenant'}
            ]
        }
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.get = mock.Mock(return_value=resp)

        rsp = sot.get_access(self.sess)

        self.sess.get.assert_called_with(
            'flavors/IDENTIFIER/os-flavor-access',
        )

        self.assertEqual(resp.body['flavor_access'], rsp)

    def test_fetch_extra_specs(self):
        sot = flavor.Flavor(**BASIC_EXAMPLE)
        resp = mock.Mock()
        resp.body = {'extra_specs': {'a': 'b', 'c': 'd'}}
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.get = mock.Mock(return_value=resp)

        rsp = sot.fetch_extra_specs(self.sess)

        self.sess.get.assert_called_with(
            'flavors/IDENTIFIER/os-extra_specs',
            microversion=self.sess.default_microversion,
        )

        self.assertEqual(resp.body['extra_specs'], rsp.extra_specs)
        self.assertIsInstance(rsp, flavor.Flavor)

    def test_create_extra_specs(self):
        sot = flavor.Flavor(**BASIC_EXAMPLE)
        specs = {'a': 'b', 'c': 'd'}
        resp = mock.Mock()
        resp.body = {'extra_specs': specs}
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.post = mock.Mock(return_value=resp)

        rsp = sot.create_extra_specs(self.sess, specs)

        self.sess.post.assert_called_with(
            'flavors/IDENTIFIER/os-extra_specs',
            json={'extra_specs': specs},
            microversion=self.sess.default_microversion,
        )

        self.assertEqual(resp.body['extra_specs'], rsp.extra_specs)
        self.assertIsInstance(rsp, flavor.Flavor)

    def test_get_extra_specs_property(self):
        sot = flavor.Flavor(**BASIC_EXAMPLE)
        resp = mock.Mock()
        resp.body = {'a': 'b'}
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.get = mock.Mock(return_value=resp)

        rsp = sot.get_extra_specs_property(self.sess, 'a')

        self.sess.get.assert_called_with(
            'flavors/IDENTIFIER/os-extra_specs/a',
            microversion=self.sess.default_microversion,
        )

        self.assertEqual('b', rsp)

    def test_update_extra_specs_property(self):
        sot = flavor.Flavor(**BASIC_EXAMPLE)
        resp = mock.Mock()
        resp.body = {'a': 'b'}
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.put = mock.Mock(return_value=resp)

        rsp = sot.update_extra_specs_property(self.sess, 'a', 'b')

        self.sess.put.assert_called_with(
            'flavors/IDENTIFIER/os-extra_specs/a',
            json={'a': 'b'},
            microversion=self.sess.default_microversion,
        )

        self.assertEqual('b', rsp)

    def test_delete_extra_specs_property(self):
        sot = flavor.Flavor(**BASIC_EXAMPLE)
        resp = mock.Mock()
        resp.body = None
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        self.sess.delete = mock.Mock(return_value=resp)

        rsp = sot.delete_extra_specs_property(self.sess, 'a')

        self.sess.delete.assert_called_with(
            'flavors/IDENTIFIER/os-extra_specs/a',
            microversion=self.sess.default_microversion,
        )

        self.assertIsNone(rsp)
