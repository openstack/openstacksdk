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
import mock

from openstack.map_reduce import map_reduce_service
from openstack.map_reduce.v1 import _proxy
from openstack.map_reduce.v1 import cluster as _cluster
from openstack.map_reduce.v1 import data_source as _ds
from openstack.map_reduce.v1 import job as _job
from openstack.map_reduce.v1 import job_binary as _jb
from openstack.map_reduce.v1 import job_exe as _exe
from openstack.map_reduce.v1 import job_execution as _je
from openstack.tests.unit.test_proxy_base3 import BaseProxyTestCase


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
        self.assertEqual(2, len(data_sources))

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


class TestJobBinary(TestMapReduceProxy):
    def __init__(self, *args, **kwargs):
        super(TestJobBinary, self).__init__(*args, **kwargs)

    def test_create_job_binary(self):
        self.mock_response_json_file_values("create_jb_response.json")

        data = {
            "name": "my-job-binary",
            "url": "/simple/mapreduce/input",
            "is_protected": False,
            "is_public": False,
            "description": "this is the job binary for map reduce job"
        }

        jb = self.proxy.create_job_binary(**data)
        self.assert_session_post_with("/job-binaries", json=data)
        self.assertIsInstance(jb, _jb.JobBinary)
        self.assertEqual("092b628b-26a3-4571-9ba4-f8d000df8877", jb.id)
        self.assertEqual("my-job-binary", jb.name)
        self.assertEqual("this is the job binary for map reduce job",
                         jb.description)
        self.assertEqual("swift://simple/mapreduce/input", jb.url)
        self.assertEqual("2017-02-28T01:46:58", jb.created_at)
        self.assertIsNone(jb.updated_at)
        self.assertFalse(jb.is_protected)
        self.assertFalse(jb.is_public)

    def test_update_job_binary(self):
        self.mock_response_json_file_values("update_jb_response.json")
        data = {
            "url": "/container/new-jar-example.jar",
            "name": "new-jar-example.jar",
            "description": "This is a new job binary"
        }
        jb = self.proxy.update_job_binary("jb-id", **data)
        self.assert_session_put_with("job-binaries/jb-id", json=data)
        self.assertIsInstance(jb, _jb.JobBinary)
        self.assertEqual("092b628b-26a3-4571-9ba4-f8d000df8877", jb.id)
        self.assertEqual("my-job-binary", jb.name)
        self.assertEqual("this is the job binary for map reduce job",
                         jb.description)
        self.assertEqual("swift://simple/mapreduce/input", jb.url)
        self.assertEqual("2017-02-28T01:46:58", jb.created_at)
        self.assertEqual("2017-02-28T02:04:01", jb.updated_at)
        self.assertFalse(jb.is_protected)
        self.assertFalse(jb.is_public)

    def test_list_job_binary(self):
        query = {
            "limit": 20,
            "sort_by": "-name",
            "marker": "jb-id"
        }
        self.mock_response_json_file_values("list_jb_response.json")
        job_binaries = list(self.proxy.job_binaries(**query))
        self.assert_session_list_with("/job-binaries", params=query)
        self.assertEqual(2, len(job_binaries))

        jb = job_binaries[0]
        self.assertIsInstance(jb, _jb.JobBinary)
        self.assertEqual("7b8298be-f6ba-4765-935b-59a3d6c0037b", jb.id)
        self.assertEqual("jarexample1.5jar", jb.name)
        self.assertEqual("swift://container/jar-example.jar", jb.url)
        self.assertEqual("This is a job binary15", jb.description)
        self.assertEqual("2017-01-17T03:04:31", jb.created_at)
        self.assertEqual("2017-02-17T03:04:31", jb.updated_at)
        self.assertEqual("3f99e3319a8943ceb15c584f3325d064", jb.tenant_id)
        self.assertTrue(jb.is_public)
        self.assertIsNone(jb.is_protected)

    def test_get_job_binary_with_id(self):
        self.mock_response_json_file_values("get_jb_response.json")
        jb = self.proxy.get_job_binary("any-jb-id")
        self.session.get.assert_called_once_with(
            "job-binaries/any-jb-id",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )
        self.assertIsInstance(jb, _jb.JobBinary)
        self.assertEqual("a716a9cd-9add-4b12-b1b6-cdb71aaef350", jb.id)
        self.assertEqual("jar-example.jar", jb.name)
        self.assertEqual("swift://container/jar-example.jar", jb.url)
        self.assertEqual("an example jar file", jb.description)
        self.assertEqual("2013-10-15 14:25:04.970513", jb.created_at)
        self.assertEqual("11587919cc534bcbb1027a161c82cf58", jb.tenant_id)
        self.assertIsNone(jb.updated_at)
        self.assertFalse(jb.is_public)
        self.assertFalse(jb.is_protected)

    def test_delete_job_binary_with_id(self):
        self.proxy.delete_job_binary("any-jb-id")
        self.assert_session_delete("job-binaries/any-jb-id")

    def test_delete_job_binary_with_instance(self):
        self.proxy.delete_job_binary(_jb.JobBinary(id="any-jb-id"))
        self.assert_session_delete("job-binaries/any-jb-id")


class TestJobs(TestMapReduceProxy):
    def __init__(self, *args, **kwargs):
        super(TestJobs, self).__init__(*args, **kwargs)

    def test_exe_job(self):
        self.mock_response_json_file_values("run_job_response.json")
        body = {
            "job_type": 1,
            "job_name": "mrs_test_jobone_20170602_141106",
            "cluster_id": "e955a7a3-d334-4943-a39a-994976900d56",
            "jar_path": "s3a://mrs-opsadm/hadoop-mapreduce.jar",
            "arguments": "wordcount",
            "input": "s3a://mrs-opsadm/input/",
            "output": "s3a://mrs-opsadm/output/",
            "job_log": "s3a://mrs-opsadm/log/",
            "file_action": "",
            "hql": "",
            "hive_script_path": ""
        }
        job_exe = self.proxy.exe_job(**body)
        self.assert_session_post_with("/jobs/submit-job", json=body)

        self.assertIsInstance(job_exe, _exe.JobExe)
        self.assertEqual(False, job_exe.templated)
        self.assertEqual(1496387588913, job_exe.created_at)
        self.assertEqual(1496387588913, job_exe.updated_at)
        self.assertEqual("12ee9ae4-6ee1-48c6-bb84-fb0b4f76cf03", job_exe.id)
        self.assertEqual("c71ad83a66c5470496c2ed6e982621cc", job_exe.tenant_id)
        self.assertEqual("", job_exe.job_id)
        self.assertEqual("mrs_test_jobone_20170602_141106", job_exe.job_name)
        self.assertEqual(None, job_exe.input_id)
        self.assertEqual(None, job_exe.output_id)
        self.assertEqual(1496387588913, job_exe.start_time)
        self.assertEqual(None, job_exe.end_time)
        self.assertEqual("e955a7a3-d334-4943-a39a-994976900d56",
                         job_exe.cluster_id)
        self.assertEqual(None, job_exe.engine_job_id)
        self.assertEqual(None, job_exe.return_code)
        self.assertEqual(None, job_exe.is_public)
        self.assertEqual(None, job_exe.is_protected)
        self.assertEqual("12ee9ae4-6ee1-48c6-bb84-fb0b4f76cf03",
                         job_exe.group_id)
        self.assertEqual(
            "s3a://mrs-opsadm/jarpath/hadoop-mapreduce-examples-2.7.2.jar",
            job_exe.jar_path
        )
        self.assertEqual("12ee9ae4-6ee1-48c6-bb84-fb0b4f76cf03",
                         job_exe.group_id)
        self.assertEqual("s3a://mrs-opsadm/input/", job_exe.input)
        self.assertEqual("s3a://mrs-opsadm/output/", job_exe.output)
        self.assertEqual("s3a://mrs-opsadm/log/", job_exe.job_log)
        self.assertEqual(1, job_exe.job_type)
        self.assertEqual("", job_exe.file_action)
        self.assertEqual("wordcount", job_exe.arguments)
        self.assertEqual("", job_exe.hql)
        self.assertEqual(2, job_exe.job_state)
        self.assertEqual(0, job_exe.job_final_status)
        self.assertEqual("", job_exe.hive_script_path)
        self.assertEqual("b67132be2f054a45b247365647e05af0", job_exe.create_by)
        self.assertEqual(0, job_exe.finished_step)
        self.assertEqual("", job_exe.job_main_id)
        self.assertEqual("", job_exe.job_step_id)
        self.assertEqual(1496387588911, job_exe.postpone_at)
        self.assertEqual("", job_exe.step_name)
        self.assertEqual(0, job_exe.step_num)
        self.assertEqual(0, job_exe.task_num)
        self.assertEqual("b67132be2f054a45b247365647e05af0", job_exe.update_by)
        self.assertEqual("", job_exe.credentials)
        self.assertEqual("b67132be2f054a45b247365647e05af0", job_exe.user_id)
        self.assertEqual(None, job_exe.job_configs)
        self.assertEqual(None, job_exe.extra)
        self.assertEqual(None, job_exe.data_source_urls)
        self.assertEqual(None, job_exe.info)

    def test_create_job(self):
        self.mock_response_json_file_values("create_job_response.json")
        data = {
            "name": "my-job",
            "mains": [],
            "libs": [
                "092b628b-26a3-4571-9ba4-f8d000df8877"
            ],
            "is_protected": False,
            "interface": [],
            "is_public": False,
            "type": "MapReduce",
            "description": "This is the Map Reduce job template"

        }
        job = self.proxy.create_job(**data)
        self.assert_session_post_with("/jobs", json=data)
        self.assertIsInstance(job, _job.Job)
        self.assertEqual("a5c1e223-e37d-4059-ad90-7a5fd35bbb68", job.id)
        self.assertEqual("my-job", job.name)
        self.assertEqual("MapReduce", job.type)
        self.assertEqual([], job.interface)
        self.assertEqual([], job.mains)
        self.assertEqual("MapReduce", job.type)
        self.assertEqual("This is the Map Reduce job template",
                         job.description)
        self.assertEqual("2016-12-09T19:44:36", job.created_at)
        self.assertEqual("46abc9f8044f40428f83a06cba0d5ddb",
                         job.tenant_id)
        self.assertIsNone(job.updated_at)
        self.assertFalse(job.is_protected)
        self.assertFalse(job.is_public)

    def test_update_job(self):
        self.mock_response_json_file_values("update_job_response.json")
        data = {
            "name": "public-pig-job-example",
            "type": "MapReduce",
            "description": "This is public pig job example",
            "mains": ["36dc7b90-d8a4-4e05-83ae-b1c03095c680"],
            "libs": [],
            "is_public": False,
            "is_protected": False
        }
        mains = [
            {
                "name": "jar-example15.jar",
                "url": "swift://container/jar-example.jar",
                "description": "This is a job binary15",
                "id": "36dc7b90-d8a4-4e05-83ae-b1c03095c680",
                "tenant_id": "3f99e3319a8943ceb15c584f3325d064",
                "is_public": True,
                "is_protected": None,
                "extra": {
                    "password": "admin",
                    "user": "admin"
                }
            }
        ]
        job = self.proxy.update_job("job-id", **data)
        self.assert_session_patch_with("jobs/job-id", json=data)
        self.assertIsInstance(job, _job.Job)
        self.assertEqual("71beddbc-9032-458b-b01e-83c515d31be2", job.id)
        self.assertEqual("my_job0001", job.name)
        self.assertEqual("MapReduce", job.type)
        self.assertEqual("This is a Map Reduce job template", job.description)
        self.assertEqual([], job.interface)
        self.assertEqual(mains, job.mains)
        self.assertEqual([], job.libs)
        self.assertEqual("2017-01-17T07:00:36", job.created_at)
        self.assertEqual("2017-02-20T10:37:25", job.updated_at)
        self.assertEqual("3f99e3319a8943ceb15c584f3325d064", job.tenant_id)
        self.assertFalse(job.is_public)
        self.assertFalse(job.is_protected)

    def test_list_job(self):
        query = {
            "limit": 20,
            "sort_by": "-name",
            "marker": "job-id"
        }
        self.mock_response_json_file_values("list_job_response.json")
        jobs = list(self.proxy.jobs(**query))
        self.assert_session_list_with("/jobs", params=query)
        self.assertEqual(2, len(jobs))

        job = jobs[0]
        self.assertIsInstance(job, _job.Job)
        self.assertEqual("66d81fda-264f-40ef-8c4f-3c65408e9611", job.id)
        self.assertEqual("my_job64552243zz44hh77", job.name)
        self.assertEqual("This is the Map Reduce job template",
                         job.description)
        self.assertEqual([], job.interface)
        self.assertEqual([], job.mains)
        self.assertEqual("2017-01-17T03:26:01", job.created_at)
        self.assertEqual("2017-01-17T03:26:01", job.updated_at)
        self.assertEqual("3f99e3319a8943ceb15c584f3325d064", job.tenant_id)
        self.assertFalse(job.is_public)
        self.assertFalse(job.is_protected)

    def test_get_job_with_id(self):
        self.mock_response_json_file_values("get_job_response.json")
        job = self.proxy.get_job("any-job-id")
        self.session.get.assert_called_once_with(
            "jobs/any-job-id",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )
        self.assertIsInstance(job, _job.Job)
        self.assertEqual("1a674c31-9aaa-4d07-b844-2bf200a1b836", job.id)
        self.assertEqual("Edp-test-job", job.name)
        self.assertEqual("MapReduce", job.type)
        self.assertEqual("", job.description)
        self.assertEqual([], job.interface)
        self.assertEqual([], job.mains)
        self.assertEqual("2015-02-10 14:25:48", job.created_at)
        self.assertIsNone(job.updated_at)
        self.assertEqual("9cd1314a0a31493282b6712b76a8fcda", job.tenant_id)
        self.assertFalse(job.is_public)
        self.assertFalse(job.is_protected)

    def test_delete_job_binary_with_id(self):
        self.proxy.delete_job("any-job-id")
        self.assert_session_delete("jobs/any-job-id")

    def test_delete_job_binary_with_instance(self):
        self.proxy.delete_job(_job.Job(id="any-job-id"))
        self.assert_session_delete("jobs/any-job-id")

    def test_execute_job(self):
        response = self.get_file_content("execute_job_response.json")
        self.mock_response_json_values(response)

        body = {
            "cluster_id": "811e1134-666f-4c48-bc92-afb5b10c9d8c",
            "input_id": "3e1bc8e6-8c69-4749-8e52-90d9341d15bc",
            "output_id": "52146b52-6540-4aac-a024-fee253cf52a9",
            "is_protected": False,
            "is_public": False,
            "job_configs": {
                "configs": {
                    "mapred.map.tasks": "1",
                    "mapred.reduce.tasks": "1"
                },
                "args": [
                    "wordcount ",
                    "arg2"
                ],
                "params": {
                    "param2": "value2",
                    "param1": "value1"
                }
            }
        }
        execution = self.proxy.execute_job("job-id", **body)
        body["job_id"] = "job-id"
        self.assert_session_post_with("jobs/job-id/execute",
                                      json=body,
                                      headers={"Accept": "application/json"})
        self.verify_execution(response["job_execution"], execution)

    def verify_execution(self, data0, execution):
        self.assertIsInstance(execution, _je.JobExecution)
        self.assertIsInstance(execution, _je.JobExecution)
        self.assertEqual(data0.get("id", None), execution.id)
        self.assertEqual(data0.get("info", None), execution.info)
        self.assertEqual(data0.get("tenant_id", None), execution.tenant_id)
        self.assertEqual(data0.get("updated_at", None), execution.updated_at)
        self.assertEqual(data0.get("created_at", None), execution.created_at)
        self.assertEqual(data0.get("end_time", None), execution.end_time)
        self.assertEqual(data0.get("start_time", None), execution.start_time)
        self.assertEqual(data0.get("is_protected", None),
                         execution.is_protected)
        self.assertEqual(data0.get("is_public", None), execution.is_public)
        self.assertEqual(data0.get("data_source_urls", None),
                         execution.data_source_urls)
        self.assertEqual(data0.get("job_configs", None), execution.job_configs)
        self.assertEqual(data0.get("job_configs", None), execution.job_configs)
        self.assertEqual(data0.get("output_id", None), execution.output_id)
        self.assertEqual(data0.get("input_id", None), execution.input_id)
        self.assertEqual(data0.get("return_code", None), execution.return_code)
        self.assertEqual(data0.get("oozie_job_id", None),
                         execution.oozie_job_id)
        self.assertEqual(data0.get("engine_job_id", None),
                         execution.engine_job_id)
        self.assertEqual(data0.get("cluster_id", None), execution.cluster_id)


class TestJobExecutions(TestMapReduceProxy):
    def __init__(self, *args, **kwargs):
        super(TestJobExecutions, self).__init__(*args, **kwargs)

    def test_list_job_execution(self):
        query = {
            "limit": 20,
            "sort_by": "-name",
            "marker": "job-id"
        }
        response = self.get_file_content("list_je_response.json")
        self.mock_response_json_values(response)
        executions = list(self.proxy.job_executions(**query))
        self.assert_session_list_with("/job-executions", params=query)
        self.assertEqual(1, len(executions))

        data0 = response["job_executions"][0]
        execution = executions[0]
        self.verify_execution(data0, execution)

    def test_get_job_execution_with_id(self):
        response = self.get_file_content("get_je_response.json")
        self.mock_response_json_values(response)
        execution = self.proxy.get_job_execution("execution-id")
        self.session.get.assert_called_once_with(
            "job-executions/execution-id",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )
        data0 = response["job_execution"]
        self.verify_execution(data0, execution)

    def verify_execution(self, data0, execution):
        self.assertIsInstance(execution, _je.JobExecution)
        self.assertIsInstance(execution, _je.JobExecution)
        self.assertEqual(data0.get("id", None), execution.id)
        self.assertEqual(data0.get("info", None), execution.info)
        self.assertEqual(data0.get("tenant_id", None), execution.tenant_id)
        self.assertEqual(data0.get("updated_at", None), execution.updated_at)
        self.assertEqual(data0.get("created_at", None), execution.created_at)
        self.assertEqual(data0.get("end_time", None), execution.end_time)
        self.assertEqual(data0.get("start_time", None), execution.start_time)
        self.assertEqual(data0.get("is_protected", None),
                         execution.is_protected)
        self.assertEqual(data0.get("is_public", None), execution.is_public)
        self.assertEqual(data0.get("data_source_urls", None),
                         execution.data_source_urls)
        self.assertEqual(data0.get("job_configs", None), execution.job_configs)
        self.assertEqual(data0.get("job_configs", None), execution.job_configs)
        self.assertEqual(data0.get("output_id", None), execution.output_id)
        self.assertEqual(data0.get("input_id", None), execution.input_id)
        self.assertEqual(data0.get("return_code", None), execution.return_code)
        self.assertEqual(data0.get("oozie_job_id", None),
                         execution.oozie_job_id)
        self.assertEqual(data0.get("engine_job_id", None),
                         execution.engine_job_id)
        self.assertEqual(data0.get("cluster_id", None), execution.cluster_id)

    def test_delete_job_execution_binary_with_id(self):
        self.proxy.delete_job_execution("execution-id")
        self.assert_session_delete("job-executions/execution-id")

    def test_delete_job_execution_binary_with_instance(self):
        self.proxy.delete_job_execution(_je.JobExecution(id="execution-id"))
        self.assert_session_delete("job-executions/execution-id")

    def test_cancel_job_execution(self):
        response = self.get_file_content("cancel_je_response.json")
        self.mock_response_json_values(response)
        execution = self.proxy.cancel_job_execution(
            _je.JobExecution(id="execution-id"))
        self.assert_session_get_with("job-executions/execution-id/cancel")
        self.verify_execution(response["job_execution"], execution)


class TestJobExe(TestMapReduceProxy):
    def __init__(self, *args, **kwargs):
        super(TestJobExe, self).__init__(*args, **kwargs)

    def test_list_job_exe(self):
        query = {
            "cluster_id": "cluster-id",
            "id": "job-exe-id",
            "job_name": "job-name",
            "state": 1
        }

        response_json = self.get_file_content("list_job_exe_response.json")
        self.response.json.side_effect = [response_json, {}]
        executions = list(self.proxy.job_exes(**query))
        self.session.get.assert_has_calls([
            mock.call("/job-exes",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      headers={"Accept": "application/json"},
                      params={"cluster_id": "cluster-id",
                              "id": "job-exe-id",
                              "job_name": "job-name",
                              "state": 1}),
            mock.call("/job-exes",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      headers={"Accept": "application/json"},
                      params={"cluster_id": "cluster-id",
                              "id": "job-exe-id",
                              "job_name": "job-name",
                              'current_page': 2,
                              'page_size': 1,
                              "state": 1})
        ])

        self.assertEqual(1, len(executions))
        execution = executions[0]

        self.assertEqual("669476bd-89d2-45aa-8f1a-872d16de377e", execution.id)
        self.assertEqual(1484641003707, execution.create_at)
        self.assertEqual(1484641003707, execution.update_at)
        self.assertEqual("3f99e3319a8943ceb15c584f3325d064",
                         execution.tenant_id)
        self.assertEqual("669476bd-89d2-45aa-8f1a-872d16de377e",
                         execution.job_id)
        self.assertEqual("myfirstjob", execution.job_name)
        self.assertEqual(1484641003707, execution.start_time)
        self.assertEqual(None, execution.end_time)
        self.assertEqual("2b460e01-3351-4170-b0a7-57b9dd5ffef3",
                         execution.cluster_id)
        self.assertEqual("669476bd-89d2-45aa-8f1a-872d16de377e",
                         execution.group_id)
        self.assertEqual(
            "s3a://jp-test1/program/hadoop-mapreduce-examples-2.4.1.jar",
            execution.jar_path)
        self.assertEqual("s3a://jp-test1/input/", execution.input)
        self.assertEqual("s3a://jp-test1/output/", execution.output)
        self.assertEqual("s3a://jp-test1/joblogs/", execution.job_log)
        self.assertEqual(1, execution.job_type)
        self.assertEqual("", execution.file_action)
        self.assertEqual("wordcount", execution.arguments)
        self.assertEqual("", execution.hql)
        self.assertEqual(2, execution.job_state)
        self.assertEqual(1, execution.job_final_status)
        self.assertEqual(None, execution.hive_script_path)
        self.assertEqual("3f99e3319a8943ceb15c584f3325d064",
                         execution.create_by)
        self.assertEqual(0, execution.finished_step)
        self.assertEqual("", execution.job_main_id)
        self.assertEqual("", execution.job_step_id)
        self.assertEqual(1484641003174, execution.postpone_at)
        self.assertEqual("", execution.step_name)
        self.assertEqual(0, execution.step_num)
        self.assertEqual(0, execution.task_num)
        self.assertEqual("3f99e3319a8943ceb15c584f3325d064",
                         execution.update_by)
        self.assertEqual(None, execution.spend_time)
        self.assertEqual(222, execution.step_seq)
        self.assertEqual("first progress", execution.progress)

    def test_get_job_exe_with_id(self):
        response = self.get_file_content("get_job_exe_response.json")
        self.mock_response_json_values(response)
        execution = self.proxy.get_job_exe("execution-id")
        self.assert_session_get_with("job-exes/execution-id")
        self.assertEqual("632863d5-15d4-4691-9dc1-1a72340cb097", execution.id)
        self.assertEqual(1484240559176, execution.create_at)
        self.assertEqual(1484240559176, execution.update_at)
        self.assertEqual("3f99e3319a8943ceb15c584f3325d064",
                         execution.tenant_id)
        self.assertEqual("632863d5-15d4-4691-9dc1-1a72340cb097",
                         execution.job_id)
        self.assertEqual("hive_script", execution.job_name)
        self.assertEqual(1484240559176, execution.start_time)
        self.assertEqual(None, execution.end_time)
        self.assertEqual("8b1d55f6-150e-45e2-8347-b2ca608d366b",
                         execution.cluster_id)

        self.assertEqual("632863d5-15d4-4691-9dc1-1a72340cb097",
                         execution.group_id)
        self.assertEqual(
            "s3a://jp-test1/program/Hivescript.sql",
            execution.jar_path)
        self.assertEqual("s3a://jp-test1/input/", execution.input)
        self.assertEqual("s3a://jp-test1/output/", execution.output)
        self.assertEqual("s3a://jp-test1/joblogs/", execution.job_log)
        self.assertEqual(3, execution.job_type)
        self.assertEqual("", execution.file_action)
        self.assertEqual("wordcount", execution.arguments)
        self.assertEqual(None, execution.hql)
        self.assertEqual(3, execution.job_state)
        self.assertEqual(1, execution.job_final_status)
        self.assertEqual("s3a://jp-test1/program/Hivescript.sql",
                         execution.hive_script_path)
        self.assertEqual("3f99e3319a8943ceb15c584f3325d064",
                         execution.create_by)
        self.assertEqual(0, execution.finished_step)
        self.assertEqual("", execution.job_main_id)
        self.assertEqual("", execution.job_step_id)
        self.assertEqual(1484240558705, execution.postpone_at)
        self.assertEqual("", execution.step_name)
        self.assertEqual(0, execution.step_num)
        self.assertEqual(0, execution.task_num)
        self.assertEqual("3f99e3319a8943ceb15c584f3325d064",
                         execution.update_by)
        self.assertEqual(None, execution.spend_time)
        self.assertEqual(222, execution.step_seq)
        self.assertEqual("first progress", execution.progress)


class TestCluster(TestMapReduceProxy):
    def __init__(self, *args, **kwargs):
        super(TestCluster, self).__init__(*args, **kwargs)

    def test_delete_cluster_with_id(self):
        self.proxy.delete_cluster("any-cluster-id")
        self.assert_session_delete("clusters/any-cluster-id")

    def test_delete_cluster_with_instance(self):
        self.proxy.delete_cluster(_cluster.Cluster(id="any-cluster-id"))
        self.assert_session_delete("clusters/any-cluster-id")

    def test_delete_cluster_with_instance2(self):
        self.proxy.delete_cluster(_cluster.ClusterInfo(id="any-cluster-id"))
        self.assert_session_delete("clusters/any-cluster-id")

    def test_expand_cluster(self):
        self.mock_response_json_values({"result": "succeeded"})
        self.proxy.expand_cluster("any-cluster-id", 2)
        self.proxy.expand_cluster(_cluster.Cluster(id="any-cluster-id"), 2)
        self.proxy.expand_cluster(_cluster.ClusterInfo(id="any-cluster-id"), 2)
        body = {
            "service_id": "",
            "plan_id": "",
            "parameters": {
                "order_id": "",
                "scale_type": "scale_out",
                "node_id": "node_orderadd",
                "instances": 2,
                "include_instances": [],
                "exclude_instances": []
            },
            "previous_values": {
                "plan_id": ""
            }
        }
        self.session.put.assert_has_calls([
            mock.call("cluster_infos/any-cluster-id",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      json=body),
            mock.call("cluster_infos/any-cluster-id",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      json=body),
            mock.call("cluster_infos/any-cluster-id",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      json=body)
        ])

    def test_reduce_cluster(self):
        self.mock_response_json_values({"result": "succeeded"})
        includes = ["instance-id-1", "instance-id-2"]
        excludes = ["instance-id-3", "instance-id-4"]
        self.proxy.reduce_cluster("any-cluster-id",
                                  3,
                                  includes=includes,
                                  excludes=excludes)
        self.proxy.reduce_cluster(_cluster.Cluster(id="any-cluster-id"),
                                  3,
                                  includes=includes,
                                  excludes=excludes)
        self.proxy.reduce_cluster(_cluster.ClusterInfo(id="any-cluster-id"),
                                  3,
                                  includes=includes,
                                  excludes=excludes)
        body = {
            "service_id": "",
            "plan_id": "",
            "parameters": {
                "order_id": "",
                "scale_type": "scale_in",
                "node_id": "node_orderadd",
                "instances": 3,
                "include_instances": includes,
                "exclude_instances": excludes
            },
            "previous_values": {
                "plan_id": ""
            }
        }
        self.session.put.assert_has_calls([
            mock.call("cluster_infos/any-cluster-id",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      json=body),
            mock.call("cluster_infos/any-cluster-id",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      json=body),
            mock.call("cluster_infos/any-cluster-id",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      json=body)
        ])

    def test_reduce_cluster2(self):
        self.mock_response_json_values({"result": "succeeded"})
        self.proxy.reduce_cluster("any-cluster-id",
                                  3)
        self.proxy.reduce_cluster(_cluster.Cluster(id="any-cluster-id"),
                                  3)
        self.proxy.reduce_cluster(_cluster.ClusterInfo(id="any-cluster-id"),
                                  3)
        body = {
            "service_id": "",
            "plan_id": "",
            "parameters": {
                "order_id": "",
                "scale_type": "scale_in",
                "node_id": "node_orderadd",
                "instances": 3,
                "include_instances": [],
                "exclude_instances": []
            },
            "previous_values": {
                "plan_id": ""
            }
        }
        self.session.put.assert_has_calls([
            mock.call("cluster_infos/any-cluster-id",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      json=body),
            mock.call("cluster_infos/any-cluster-id",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      json=body),
            mock.call("cluster_infos/any-cluster-id",
                      endpoint_filter=self.service,
                      endpoint_override=self.service.get_endpoint_override(),
                      json=body)
        ])

    def test_create_cluster_and_run_job(self):
        self.mock_response_json_values({
            "cluster_id": "da1592c2-bb7e-468d-9ac9-83246e95447a",
            "result": True,
            "msg": ""
        })

        cluster = self.get_file_content("create_cluster_request.json")
        job = {
            "job_type": 1,
            "job_name": "tenji111",
            "jar_path": "s3a://bigdata/examples.jar",
            "arguments": "wordcount",
            "input": "s3a://bigdata/input/wd_1k/",
            "output": "s3a://bigdata/ouput/",
            "job_log": "s3a://bigdata/log/",
            "shutdown_cluster": True,
            "file_action": "",
            "submit_job_once_cluster_run": True,
            "hql": "",
            "hive_script_path": ""
        }
        result = self.proxy.create_cluster_and_run_job(cluster, job)
        cluster["add_jobs"] = [job]
        self.assert_session_post_with("/run-job-flow", dict(cluster))
        self.assertEqual("da1592c2-bb7e-468d-9ac9-83246e95447a", result.id)
        self.assertEqual("newcluster", result.name)

    def test_get_cluster(self):
        self.mock_response_json_file_values("get_cluster_response.json")
        cluster = self.proxy.get_cluster("any-cluster-id")
        self.session.get.assert_called_once_with(
            "cluster_infos/any-cluster-id",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )
        self.assertIsInstance(cluster, _cluster.ClusterDetail)
        self.assertEqual("bdb064ff-2855-4624-90d5-e9a6376abd6e", cluster.id)
        self.assertEqual(2, cluster.master_node_num)
        self.assertEqual(3, cluster.core_node_num)
        self.assertEqual("scaling-in", cluster.state)
        self.assertEqual("1487570757", cluster.create_at)
        self.assertEqual("1487668974", cluster.update_at)
        self.assertEqual("Metered", cluster.billing_type)
        self.assertEqual("eu-de", cluster.data_center)
        self.assertEqual("20161218", cluster.vpc_name)
        self.assertEqual("0", cluster.duration)
        self.assertEqual("0", cluster.fee)
        self.assertEqual("", cluster.hadoop_version)
        self.assertEqual("c2.2xlarge.linux.mrs", cluster.master_node_size)
        self.assertEqual("c2.2xlarge.linux.mrs", cluster.core_node_size)
        self.assertEqual("100.64.49.9", cluster.external_ip)
        self.assertEqual("100.64.49.13", cluster.external_alternate_ip)
        self.assertEqual("192.168.1.242", cluster.internal_ip)
        self.assertEqual("4ac46ca7-a488-4b91-82c2-e4d7aa9c40c2",
                         cluster.deployment_id)
        self.assertEqual("", cluster.remark)
        self.assertEqual("HWS001015A5A1E845A0", cluster.order_id)
        self.assertEqual("1d7b939b382c4c3bb3481a8ca10da768",
                         cluster.availability_zone_id)
        self.assertEqual("b35cf2d2348a445ca74b32289a160882",
                         cluster.master_node_product_id)
        self.assertEqual("8ab05e503b4c42abb304e2489560063b",
                         cluster.master_node_spec_id)
        self.assertEqual("dc970349d128460e960a0c2b826c427c",
                         cluster.core_node_product_id)
        self.assertEqual("cdc6035a249a40249312f5ef72a23cd7",
                         cluster.core_node_spec_id)
        self.assertEqual("eu-de-01", cluster.availability_zone)
        self.assertEqual("4ac46ca7-a488-4b91-82c2-e4d7aa9c40c2",
                         cluster.instance_id)
        self.assertEqual(None, cluster.vnc)
        self.assertEqual("3f99e3319a8943ceb15c584f3325d064", cluster.tenant_id)
        self.assertEqual(100, cluster.volume_size)
        self.assertEqual("SATA", cluster.volume_type)
        self.assertEqual("subnet", cluster.subnet_name)
        self.assertEqual("930e34e2-195d-401f-af07-0b64ea6603f8",
                         cluster.security_groups_id)
        self.assertEqual("2ef3343e-3477-4a0d-80fe-4d874e4f81b8",
                         cluster.slave_security_groups_id)
        self.assertEqual(1, cluster.safe_mode)
        self.assertEqual("FusionInsight V100R002C61", cluster.version)
        self.assertEqual("myp", cluster.keypair)
        self.assertEqual("192.168.1.242", cluster.master_node_ip)
        self.assertEqual("192.168.1.234", cluster.private_ip_first)
        self.assertEqual(None, cluster.error_info)
        self.assertEqual("0", cluster.charging_start_time)
        self.assertEqual(4, len(cluster.component_list))
        self.assertEqual({
            "componentId": "MRS 1.3.0_001",
            "componentName": "Hadoop",
            "componentVersion": "2.7.2",
            "componentDesc": "desc"
        }, cluster.component_list[0])
