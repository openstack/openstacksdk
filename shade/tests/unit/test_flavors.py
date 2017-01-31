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


import shade
from shade.tests.unit import base

FLAVOR_ID = '0c1d9008-f546-4608-9e8f-f8bdaec8dddd'
ENDPOINT = 'https://compute.example.com/v2.1/1c36b64c840a42cd9e9b931a369337f0'
FAKE_FLAVOR = {
    u'OS-FLV-DISABLED:disabled': False,
    u'OS-FLV-EXT-DATA:ephemeral': 0,
    u'disk': 1600,
    u'id': u'0c1d9008-f546-4608-9e8f-f8bdaec8dddd',
    u'links': [{
        u'href': u'{endpoint}/flavors/{id}'.format(
            endpoint=ENDPOINT, id=FLAVOR_ID),
        u'rel': u'self'
    }, {
        u'href': u'{endpoint}/flavors/{id}'.format(
            endpoint=ENDPOINT, id=FLAVOR_ID),
        u'rel': u'bookmark'
    }],
    u'name': u'vanilla',
    u'os-flavor-access:is_public': True,
    u'ram': 65536,
    u'rxtx_factor': 1.0,
    u'swap': u'',
    u'vcpus': 24
}
FAKE_FLAVOR_LIST = [FAKE_FLAVOR]


class TestFlavors(base.RequestsMockTestCase):

    def test_create_flavor(self):

        self.register_uri(
            'POST', '{endpoint}/flavors'.format(
                endpoint=ENDPOINT),
            json={'flavor': FAKE_FLAVOR},
            validate=dict(
                json={'flavor': {
                    "name": "vanilla",
                    "ram": 65536,
                    "vcpus": 24,
                    "swap": 0,
                    "os-flavor-access:is_public": True,
                    "rxtx_factor": 1.0,
                    "OS-FLV-EXT-DATA:ephemeral": 0,
                    "disk": 1600,
                    "id": None
                }}))

        self.register_uri(
            'GET', '{endpoint}/flavors/{id}'.format(
                endpoint=ENDPOINT, id=FLAVOR_ID),
            json={'flavor': FAKE_FLAVOR})

        self.op_cloud.create_flavor(
            'vanilla', ram=65536, disk=1600, vcpus=24,
        )
        self.assert_calls()

    def test_delete_flavor(self):
        self.register_uri(
            'GET', '{endpoint}/flavors/detail?is_public=None'.format(
                endpoint=ENDPOINT),
            json={'flavors': FAKE_FLAVOR_LIST})
        self.register_uri(
            'DELETE', '{endpoint}/flavors/{id}'.format(
                endpoint=ENDPOINT, id=FLAVOR_ID))
        self.assertTrue(self.op_cloud.delete_flavor('vanilla'))

        self.assert_calls()

    def test_delete_flavor_not_found(self):
        self.register_uri(
            'GET', '{endpoint}/flavors/detail?is_public=None'.format(
                endpoint=ENDPOINT),
            json={'flavors': []})

        self.assertFalse(self.op_cloud.delete_flavor('invalid'))

        self.assert_calls()

    def test_delete_flavor_exception(self):
        self.register_uri(
            'GET', '{endpoint}/flavors/detail?is_public=None'.format(
                endpoint=ENDPOINT),
            json={'flavors': FAKE_FLAVOR_LIST})
        self.register_uri(
            'DELETE', '{endpoint}/flavors/{id}'.format(
                endpoint=ENDPOINT, id=FLAVOR_ID),
            status_code=503)
        self.assertRaises(shade.OpenStackCloudException,
                          self.op_cloud.delete_flavor, 'vanilla')

    def test_list_flavors(self):
        self.register_uri(
            'GET', '{endpoint}/flavors/detail?is_public=None'.format(
                endpoint=ENDPOINT),
            json={'flavors': FAKE_FLAVOR_LIST})
        self.register_uri(
            'GET', '{endpoint}/flavors/{id}/os-extra_specs'.format(
                endpoint=ENDPOINT, id=FLAVOR_ID),
            json={'extra_specs': {}})

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

    def test_set_flavor_specs(self):
        extra_specs = dict(key1='value1')
        self.register_uri(
            'POST', '{endpoint}/flavors/{id}/os-extra_specs'.format(
                endpoint=ENDPOINT, id=1),
            json=dict(extra_specs=extra_specs))

        self.op_cloud.set_flavor_specs(1, extra_specs)
        self.assert_calls()

    def test_unset_flavor_specs(self):
        keys = ['key1', 'key2']
        for key in keys:
            self.register_uri(
                'DELETE',
                '{endpoint}/flavors/{id}/os-extra_specs/{key}'.format(
                    endpoint=ENDPOINT, id=1, key=key))

        self.op_cloud.unset_flavor_specs(1, keys)
        self.assert_calls()

    def test_add_flavor_access(self):
        self.register_uri(
            'POST', '{endpoint}/flavors/{id}/action'.format(
                endpoint=ENDPOINT, id='flavor_id'),
            json={
                'flavor_access': [{
                    'flavor_id': 'flavor_id',
                    'tenant_id': 'tenant_id',
                }]},
            validate=dict(
                json={
                    'addTenantAccess': {
                        'tenant': 'tenant_id',
                    }}))

        self.op_cloud.add_flavor_access('flavor_id', 'tenant_id')
        self.assert_calls()

    def test_remove_flavor_access(self):
        self.register_uri(
            'POST', '{endpoint}/flavors/{id}/action'.format(
                endpoint=ENDPOINT, id='flavor_id'),
            json={'flavor_access': []},
            validate=dict(
                json={
                    'removeTenantAccess': {
                        'tenant': 'tenant_id',
                    }}))

        self.op_cloud.remove_flavor_access('flavor_id', 'tenant_id')
        self.assert_calls()

    def test_list_flavor_access(self):
        self.register_uri(
            'GET', '{endpoint}/flavors/vanilla/os-flavor-access'.format(
                endpoint=ENDPOINT),
            json={
                'flavor_access': [{
                    'flavor_id': 'vanilla',
                    'tenant_id': 'tenant_id',
                }]})
        self.op_cloud.list_flavor_access('vanilla')
        self.assert_calls()
