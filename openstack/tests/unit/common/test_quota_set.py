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

from keystoneauth1 import adapter

from openstack.common import quota_set as _qs
from openstack.tests.unit import base


BASIC_EXAMPLE = {
    "backup_gigabytes": 1000,
    "backups": 10,
    "gigabytes___DEFAULT__": -1,
}

USAGE_EXAMPLE = {
    "backup_gigabytes": {"in_use": 0, "limit": 1000, "reserved": 0},
    "backups": {"in_use": 0, "limit": 10, "reserved": 0},
    "gigabytes___DEFAULT__": {"in_use": 0, "limit": -1, "reserved": 0},
}


class TestQuotaSet(base.TestCase):
    def setUp(self):
        super().setUp()
        self.sess = mock.Mock(spec=adapter.Adapter)
        self.sess.default_microversion = 1
        self.sess._get_connection = mock.Mock(return_value=self.cloud)
        self.sess.retriable_status_codes = set()

    def test_basic(self):
        sot = _qs.QuotaSet()
        self.assertEqual('quota_set', sot.resource_key)
        self.assertIsNone(sot.resources_key)
        self.assertEqual('/os-quota-sets/%(project_id)s', sot.base_path)
        self.assertTrue(sot.allow_create)
        self.assertTrue(sot.allow_fetch)
        self.assertTrue(sot.allow_delete)
        self.assertFalse(sot.allow_list)
        self.assertTrue(sot.allow_commit)

        self.assertDictEqual(
            {"usage": "usage", "limit": "limit", "marker": "marker"},
            sot._query_mapping._mapping,
        )

    def test_make_basic(self):
        sot = _qs.QuotaSet(**BASIC_EXAMPLE)

        self.assertEqual(BASIC_EXAMPLE['backups'], sot.backups)

    def test_get(self):
        sot = _qs.QuotaSet(project_id='proj')

        resp = mock.Mock()
        resp.body = {'quota_set': copy.deepcopy(BASIC_EXAMPLE)}
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        resp.headers = {}
        self.sess.get = mock.Mock(return_value=resp)

        sot.fetch(self.sess)

        self.sess.get.assert_called_with(
            '/os-quota-sets/proj', microversion=1, params={}, skip_cache=False
        )

        self.assertEqual(BASIC_EXAMPLE['backups'], sot.backups)
        self.assertEqual({}, sot.reservation)
        self.assertEqual({}, sot.usage)

    def test_get_usage(self):
        sot = _qs.QuotaSet(project_id='proj')

        resp = mock.Mock()
        resp.body = {'quota_set': copy.deepcopy(USAGE_EXAMPLE)}
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        resp.headers = {}
        self.sess.get = mock.Mock(return_value=resp)

        sot.fetch(self.sess, usage=True)

        self.sess.get.assert_called_with(
            '/os-quota-sets/proj',
            microversion=1,
            params={'usage': True},
            skip_cache=False,
        )

        self.assertEqual(USAGE_EXAMPLE['backups']['limit'], sot.backups)

    def test_update_quota(self):
        # Use QuotaSet as if it was returned by get(usage=True)
        sot = _qs.QuotaSet.existing(
            project_id='proj',
            reservation={'a': 'b'},
            usage={'c': 'd'},
            foo='bar',
        )

        resp = mock.Mock()
        resp.body = {'quota_set': copy.deepcopy(BASIC_EXAMPLE)}
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        resp.headers = {}
        self.sess.put = mock.Mock(return_value=resp)

        sot._update(reservation={'b': 'd'}, backups=15, something_else=20)

        sot.commit(self.sess)

        self.sess.put.assert_called_with(
            '/os-quota-sets/proj',
            microversion=1,
            headers={},
            json={'quota_set': {'backups': 15, 'something_else': 20}},
        )

    def test_delete_quota(self):
        # Use QuotaSet as if it was returned by get(usage=True)
        sot = _qs.QuotaSet.existing(
            project_id='proj',
            reservation={'a': 'b'},
            usage={'c': 'd'},
            foo='bar',
        )

        resp = mock.Mock()
        resp.body = None
        resp.json = mock.Mock(return_value=resp.body)
        resp.status_code = 200
        resp.headers = {}
        self.sess.delete = mock.Mock(return_value=resp)

        sot.delete(self.sess)

        self.sess.delete.assert_called_with(
            '/os-quota-sets/proj',
            microversion=1,
            headers={},
        )
