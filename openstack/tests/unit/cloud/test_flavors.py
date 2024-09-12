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

from openstack import exceptions
from openstack.tests import fakes
from openstack.tests.unit import base


class TestFlavors(base.TestCase):
    def setUp(self):
        super().setUp()
        # self.use_compute_discovery()

    def test_create_flavor(self):
        self.use_compute_discovery()
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors',
                    json={'flavor': fakes.FAKE_FLAVOR},
                    validate=dict(
                        json={
                            'flavor': {
                                "name": "vanilla",
                                "description": None,
                                "ram": 65536,
                                "vcpus": 24,
                                "swap": 0,
                                "os-flavor-access:is_public": True,
                                "rxtx_factor": 1.0,
                                "OS-FLV-EXT-DATA:ephemeral": 0,
                                "disk": 1600,
                                "id": None,
                            }
                        }
                    ),
                )
            ]
        )

        self.cloud.create_flavor(
            'vanilla',
            ram=65536,
            disk=1600,
            vcpus=24,
        )
        self.assert_calls()

    def test_delete_flavor(self):
        self.use_compute_discovery()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/vanilla',
                    json=fakes.FAKE_FLAVOR,
                ),
                dict(
                    method='DELETE',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/{fakes.FLAVOR_ID}',
                ),
            ]
        )
        self.assertTrue(self.cloud.delete_flavor('vanilla'))

        self.assert_calls()

    def test_delete_flavor_not_found(self):
        self.use_compute_discovery()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/invalid',
                    status_code=404,
                ),
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/detail?is_public=None',
                    json={'flavors': fakes.FAKE_FLAVOR_LIST},
                ),
            ]
        )

        self.assertFalse(self.cloud.delete_flavor('invalid'))

        self.assert_calls()

    def test_delete_flavor_exception(self):
        self.use_compute_discovery()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/vanilla',
                    json=fakes.FAKE_FLAVOR,
                ),
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/detail?is_public=None',
                    json={'flavors': fakes.FAKE_FLAVOR_LIST},
                ),
                dict(
                    method='DELETE',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/{fakes.FLAVOR_ID}',
                    status_code=503,
                ),
            ]
        )

        self.assertRaises(
            exceptions.SDKException,
            self.cloud.delete_flavor,
            'vanilla',
        )

    def test_list_flavors(self):
        self.use_compute_discovery()
        uris_to_mock = [
            dict(
                method='GET',
                uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/detail?is_public=None',
                json={'flavors': fakes.FAKE_FLAVOR_LIST},
            ),
        ]
        self.register_uris(uris_to_mock)

        flavors = self.cloud.list_flavors()

        # test that new flavor is created correctly
        found = False
        for flavor in flavors:
            if flavor['name'] == 'vanilla':
                found = True
                break
        self.assertTrue(found)
        needed_keys = {'name', 'ram', 'vcpus', 'id', 'is_public', 'disk'}
        if found:
            # check flavor content
            self.assertTrue(needed_keys.issubset(flavor.keys()))
        self.assert_calls()

    def test_list_flavors_with_extra(self):
        self.use_compute_discovery()
        uris_to_mock = [
            dict(
                method='GET',
                uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/detail?is_public=None',
                json={'flavors': fakes.FAKE_FLAVOR_LIST},
            ),
        ]
        uris_to_mock.extend(
            [
                dict(
                    method='GET',
                    uri='{endpoint}/flavors/{id}/os-extra_specs'.format(
                        endpoint=fakes.COMPUTE_ENDPOINT, id=flavor['id']
                    ),
                    json={'extra_specs': {}},
                )
                for flavor in fakes.FAKE_FLAVOR_LIST
            ]
        )
        self.register_uris(uris_to_mock)

        flavors = self.cloud.list_flavors(get_extra=True)

        # test that new flavor is created correctly
        found = False
        for flavor in flavors:
            if flavor['name'] == 'vanilla':
                found = True
                break
        self.assertTrue(found)
        needed_keys = {'name', 'ram', 'vcpus', 'id', 'is_public', 'disk'}
        if found:
            # check flavor content
            self.assertTrue(needed_keys.issubset(flavor.keys()))
        self.assert_calls()

    def test_get_flavor_by_ram(self):
        self.use_compute_discovery()
        uris_to_mock = [
            dict(
                method='GET',
                uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/detail?is_public=None',
                json={'flavors': fakes.FAKE_FLAVOR_LIST},
            ),
        ]
        uris_to_mock.extend(
            [
                dict(
                    method='GET',
                    uri='{endpoint}/flavors/{id}/os-extra_specs'.format(
                        endpoint=fakes.COMPUTE_ENDPOINT, id=flavor['id']
                    ),
                    json={'extra_specs': {}},
                )
                for flavor in fakes.FAKE_FLAVOR_LIST
            ]
        )
        self.register_uris(uris_to_mock)

        flavor = self.cloud.get_flavor_by_ram(ram=250)
        self.assertEqual(fakes.STRAWBERRY_FLAVOR_ID, flavor['id'])

    def test_get_flavor_by_ram_and_include(self):
        self.use_compute_discovery()
        uris_to_mock = [
            dict(
                method='GET',
                uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/detail?is_public=None',
                json={'flavors': fakes.FAKE_FLAVOR_LIST},
            ),
        ]
        uris_to_mock.extend(
            [
                dict(
                    method='GET',
                    uri='{endpoint}/flavors/{id}/os-extra_specs'.format(
                        endpoint=fakes.COMPUTE_ENDPOINT, id=flavor['id']
                    ),
                    json={'extra_specs': {}},
                )
                for flavor in fakes.FAKE_FLAVOR_LIST
            ]
        )
        self.register_uris(uris_to_mock)
        flavor = self.cloud.get_flavor_by_ram(ram=150, include='strawberry')
        self.assertEqual(fakes.STRAWBERRY_FLAVOR_ID, flavor['id'])

    def test_get_flavor_by_ram_not_found(self):
        self.use_compute_discovery()
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/detail?is_public=None',
                    json={'flavors': []},
                )
            ]
        )
        self.assertRaises(
            exceptions.SDKException,
            self.cloud.get_flavor_by_ram,
            ram=100,
        )

    def test_get_flavor_string_and_int(self):
        self.use_compute_discovery()
        flavor_resource_uri = (
            f'{fakes.COMPUTE_ENDPOINT}/flavors/1/os-extra_specs'
        )
        flavor = fakes.make_fake_flavor('1', 'vanilla')
        flavor_json = {'extra_specs': {}}

        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/1',
                    json=flavor,
                ),
                dict(method='GET', uri=flavor_resource_uri, json=flavor_json),
            ]
        )

        flavor1 = self.cloud.get_flavor('1')
        self.assertEqual('1', flavor1['id'])
        flavor2 = self.cloud.get_flavor(1)
        self.assertEqual('1', flavor2['id'])

    def test_set_flavor_specs(self):
        self.use_compute_discovery()
        extra_specs = dict(key1='value1')
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/{1}/os-extra_specs',
                    json=dict(extra_specs=extra_specs),
                )
            ]
        )

        self.cloud.set_flavor_specs(1, extra_specs)
        self.assert_calls()

    def test_unset_flavor_specs(self):
        self.use_compute_discovery()
        keys = ['key1', 'key2']
        self.register_uris(
            [
                dict(
                    method='DELETE',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/{1}/os-extra_specs/{key}',
                )
                for key in keys
            ]
        )

        self.cloud.unset_flavor_specs(1, keys)
        self.assert_calls()

    def test_add_flavor_access(self):
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri='{endpoint}/flavors/{id}/action'.format(
                        endpoint=fakes.COMPUTE_ENDPOINT, id='flavor_id'
                    ),
                    json={
                        'flavor_access': [
                            {
                                'flavor_id': 'flavor_id',
                                'tenant_id': 'tenant_id',
                            }
                        ]
                    },
                    validate=dict(
                        json={'addTenantAccess': {'tenant': 'tenant_id'}}
                    ),
                )
            ]
        )

        self.cloud.add_flavor_access('flavor_id', 'tenant_id')
        self.assert_calls()

    def test_remove_flavor_access(self):
        self.register_uris(
            [
                dict(
                    method='POST',
                    uri='{endpoint}/flavors/{id}/action'.format(
                        endpoint=fakes.COMPUTE_ENDPOINT, id='flavor_id'
                    ),
                    json={'flavor_access': []},
                    validate=dict(
                        json={'removeTenantAccess': {'tenant': 'tenant_id'}}
                    ),
                )
            ]
        )

        self.cloud.remove_flavor_access('flavor_id', 'tenant_id')
        self.assert_calls()

    def test_list_flavor_access(self):
        self.register_uris(
            [
                dict(
                    method='GET',
                    uri=f'{fakes.COMPUTE_ENDPOINT}/flavors/vanilla/os-flavor-access',
                    json={
                        'flavor_access': [
                            {'flavor_id': 'vanilla', 'tenant_id': 'tenant_id'}
                        ]
                    },
                )
            ]
        )
        self.cloud.list_flavor_access('vanilla')
        self.assert_calls()

    def test_get_flavor_by_id(self):
        self.use_compute_discovery()
        flavor_uri = f'{fakes.COMPUTE_ENDPOINT}/flavors/1'
        flavor_json = {'flavor': fakes.make_fake_flavor('1', 'vanilla')}

        self.register_uris(
            [
                dict(method='GET', uri=flavor_uri, json=flavor_json),
            ]
        )

        flavor1 = self.cloud.get_flavor_by_id('1')
        self.assertEqual('1', flavor1['id'])
        self.assertEqual({}, flavor1.extra_specs)
        flavor2 = self.cloud.get_flavor_by_id('1')
        self.assertEqual('1', flavor2['id'])
        self.assertEqual({}, flavor2.extra_specs)

    def test_get_flavor_with_extra_specs(self):
        self.use_compute_discovery()
        flavor_uri = f'{fakes.COMPUTE_ENDPOINT}/flavors/1'
        flavor_extra_uri = f'{fakes.COMPUTE_ENDPOINT}/flavors/1/os-extra_specs'
        flavor_json = {'flavor': fakes.make_fake_flavor('1', 'vanilla')}
        flavor_extra_json = {'extra_specs': {'name': 'test'}}

        self.register_uris(
            [
                dict(method='GET', uri=flavor_uri, json=flavor_json),
                dict(
                    method='GET', uri=flavor_extra_uri, json=flavor_extra_json
                ),
            ]
        )

        flavor1 = self.cloud.get_flavor_by_id('1', get_extra=True)
        self.assertEqual('1', flavor1['id'])
        self.assertEqual({'name': 'test'}, flavor1.extra_specs)
        flavor2 = self.cloud.get_flavor_by_id('1', get_extra=False)
        self.assertEqual('1', flavor2['id'])
        self.assertEqual({}, flavor2.extra_specs)
