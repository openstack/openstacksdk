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

from openstack.compute.v2 import aggregate
from openstack.tests.unit import base

IDENTIFIER = 'IDENTIFIER'

EXAMPLE = {
    "name": "m-family",
    "availability_zone": None,
    "deleted": False,
    "created_at": "2018-07-06T14:58:16.000000",
    "updated_at": None,
    "hosts": ["oscomp-m001", "oscomp-m002", "oscomp-m003"],
    "deleted_at": None,
    "id": 4,
    "uuid": IDENTIFIER,
    "metadata": {"type": "public", "family": "m-family"},
}


class TestAggregate(base.TestCase):
    def setUp(self):
        super().setUp()
        self.resp = mock.Mock()
        self.resp.body = EXAMPLE.copy()
        self.resp.json = mock.Mock(return_value=self.resp.body)
        self.resp.status_code = 200
        self.resp.headers = {'Accept': ''}
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.post = mock.Mock(return_value=self.resp)

    def test_basic(self):
        sot = aggregate.Aggregate()
        self.assertEqual('aggregate', sot.resource_key)
        self.assertEqual('aggregates', sot.resources_key)
        self.assertEqual('/os-aggregates', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_commit)
        self.assertTrue(sot.allow_delete)
        self.assertTrue(sot.allow_list)

    def test_make_it(self):
        sot = aggregate.Aggregate(**EXAMPLE)
        self.assertEqual(EXAMPLE['name'], sot.name)
        self.assertEqual(EXAMPLE['availability_zone'], sot.availability_zone)
        self.assertEqual(EXAMPLE['deleted'], sot.is_deleted)
        self.assertEqual(EXAMPLE['deleted_at'], sot.deleted_at)
        self.assertEqual(EXAMPLE['created_at'], sot.created_at)
        self.assertEqual(EXAMPLE['updated_at'], sot.updated_at)
        self.assertEqual(EXAMPLE['hosts'], sot.hosts)
        self.assertEqual(EXAMPLE['id'], sot.id)
        self.assertEqual(EXAMPLE['uuid'], sot.uuid)
        self.assertDictEqual(EXAMPLE['metadata'], sot.metadata)

    def test_add_host(self):
        sot = aggregate.Aggregate(**EXAMPLE)

        sot.add_host(self.sess, 'host1')

        url = 'os-aggregates/4/action'
        body = {"add_host": {"host": "host1"}}
        self.sess.post.assert_called_with(url, json=body, microversion=None)

    def test_remove_host(self):
        sot = aggregate.Aggregate(**EXAMPLE)

        sot.remove_host(self.sess, 'host1')

        url = 'os-aggregates/4/action'
        body = {"remove_host": {"host": "host1"}}
        self.sess.post.assert_called_with(url, json=body, microversion=None)

    def test_set_metadata(self):
        sot = aggregate.Aggregate(**EXAMPLE)

        sot.set_metadata(self.sess, {"key: value"})

        url = 'os-aggregates/4/action'
        body = {"set_metadata": {"metadata": {"key: value"}}}
        self.sess.post.assert_called_with(url, json=body, microversion=None)

    def test_precache_image(self):
        sot = aggregate.Aggregate(**EXAMPLE)

        sot.precache_images(self.sess, ['1'])

        url = 'os-aggregates/4/images'
        body = {"cache": ['1']}
        self.sess.post.assert_called_with(
            url, json=body, microversion=sot._max_microversion
        )
