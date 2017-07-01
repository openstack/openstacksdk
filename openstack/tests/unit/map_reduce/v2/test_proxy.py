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

from openstack.tests.unit.test_proxy_base3 import BaseProxyTestCase
from openstack.map_reduce import map_reduce_service
from openstack.map_reduce.v1 import _proxy
from openstack.map_reduce.v1 import data_source as _ds
from openstack.map_reduce.v1 import job_binary as _jb
from openstack.map_reduce.v1 import job as _job


class TestMapReduceProxy(BaseProxyTestCase):
    def __init__(self, *args, **kwargs):
        super(TestMapReduceProxy, self).__init__(
            *args,
            proxy_class=_proxy.Proxy,
            service_class=map_reduce_service.MapReduceService,
            **kwargs)


class TestDataSource(TestMapReduceProxy):
    def __init__(self, *args, **kwargs):
        super(TestDataSource, self).__init__(*args, **kwargs)

    def test_create_data_source(self):
        self.mock_response_json_file_values("create_ds_response.json")

        data = {
            "name": "ds-input-1",
            "url": "/simple/mapreduce/input",
            "is_protected": False,
            "is_public": False,
            "type": "hdfs",
            "description": "input for unittest"
        }

        ds = self.proxy.create_data_source(**data)
        self.assert_session_post_with("/data-sources", json=data)
        self.assertIsInstance(ds, _ds.DataSource)
        self.assertEqual("9bcd0e98-d927-4cae-a111-c30ebc2454ed", ds.id)
        self.assertEqual("my-input", ds.name)
        self.assertEqual("hdfs", ds.type)
        self.assertEqual("", ds.description)
        self.assertEqual("/simple/mapreduce/input", ds.url)
        self.assertEqual("46abc9f8044f40428f83a06cba0d5ddb", ds.tenant_id)
        self.assertEqual("2016-12-09T19:12:14", ds.created_at)
        self.assertEqual("2016-12-09T19:12:14", ds.updated_at)
        self.assertFalse(ds.is_protected)
        self.assertFalse(ds.is_public)

    def test_update_data_source(self):
        self.mock_response_json_file_values("update_ds_response.json")
        data = {
            "name": "hdfs_input19",
            "type": "hdfs",
            "url": "/test-master-node:8020/user/hadoop/input",
            "description": "This is public input",
            "is_protected": True
        }
        ds = self.proxy.update_data_source("ds-id", **data)
        self.assert_session_put_with("data-sources/ds-id", json=data)
        self.assertIsInstance(ds, _ds.DataSource)
        self.assertEqual("9bcd0e98-d927-4cae-a111-c30ebc2454ed", ds.id)
        self.assertEqual("my-input", ds.name)
        self.assertEqual("hdfs", ds.type)
        self.assertEqual("", ds.description)
        self.assertEqual("/simple/mapreduce/input", ds.url)
        self.assertEqual("46abc9f8044f40428f83a06cba0d5ddb", ds.tenant_id)
        self.assertEqual("2016-12-09T19:12:14", ds.created_at)
        self.assertEqual("2016-12-14T09:05:44", ds.updated_at)
        self.assertFalse(ds.is_protected)
        self.assertFalse(ds.is_public)

    def test_list_data_source(self):
        query = {
            "limit": 20,
            "sort_by": "-name",
            "marker": "ds-id"
        }
        self.mock_response_json_file_values("list_ds.json")
        data_sources = list(self.proxy.data_sources(**query))
        self.assert_session_list_with("/data-sources", params=query)
        self.assertEquals(2, len(data_sources))

        ds = data_sources[0]
        self.assertIsInstance(ds, _ds.DataSource)
        self.assertEqual("fba9bae4-dabf-4ac1-8511-db80c7ad2e5c", ds.id)
        self.assertEqual("hdfs_input13", ds.name)
        self.assertEqual("hdfs", ds.type)
        self.assertEqual("/test-master-node:8020/user/hadoop/input",
                         ds.url)
        self.assertEqual("This is hdfs input13_testtest", ds.description)
        self.assertEqual("2016-12-09T19:12:14", ds.created_at)
        self.assertEqual("3f99e3319a8943ceb15c584f3325d064", ds.tenant_id)
        self.assertIsNone(ds.updated_at)
        self.assertIsNone(ds.is_public)
        self.assertIsNone(ds.is_protected)

    def test_get_data_source_with_id(self):
        self.mock_response_json_file_values("get_ds.json")
        ds = self.proxy.get_data_source("any-ds-id")
        self.session.get.assert_called_once_with(
            "data-sources/any-ds-id",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )
        self.assertIsInstance(ds, _ds.DataSource)
        self.assertEqual("953831f2-0852-49d8-ac71-af5805e25256", ds.id)
        self.assertEqual("swift_input", ds.name)
        self.assertEqual("hdfs", ds.type)
        self.assertEqual("/container/text", ds.url)
        self.assertEqual("This is input", ds.description)
        self.assertEqual("2016-12-09T19:12:14", ds.created_at)
        self.assertEqual("9cd1314a0a31493282b6712b76a8fcda", ds.tenant_id)
        self.assertIsNone(ds.updated_at)
        self.assertFalse(ds.is_public)
        self.assertFalse(ds.is_protected)

    def test_delete_data_source_with_id(self):
        self.proxy.delete_data_source("any-ds-id")
        self.assert_session_delete("data-sources/any-ds-id")

    def test_delete_data_source_with_instance(self):
        self.proxy.delete_data_source(_ds.DataSource(id="any-ds-id"))
        self.assert_session_delete("data-sources/any-ds-id")
