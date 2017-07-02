class TestJobExecutions(TestMapReduceProxy):
    def __init__(self, *args, **kwargs):
        super(TestJobExecutions, self).__init__(*args, **kwargs)

    def test_list_job_execution(self):
        query = {
            "limit": 20,
            "sort_by": "-name",
            "marker": "job-id"
        }
        self.mock_response_json_file_values("list_job_execution_response.json")
        jobs = list(self.proxy.jobs(**query))
        self.assert_session_list_with("/jobs", params=query)
        self.assertEquals(2, len(jobs))

        job = jobs[0]
        self.assertIsInstance(job, _je.JobExecution)
        self.assertEqual("66d81fda-264f-40ef-8c4f-3c65408e9611", job.id)
        self.assertEqual("my_job_execution64552243zz44hh77", job.name)
        self.assertEqual("This is the Map Reduce job template",
                         job.description)
        self.assertEqual([], job.interface)
        self.assertEqual([], job.mains)
        self.assertEqual("2017-01-17T03:26:01", job.created_at)
        self.assertEqual("2017-01-17T03:26:01", job.updated_at)
        self.assertEqual("3f99e3319a8943ceb15c584f3325d064", job.tenant_id)
        self.assertFalse(job.is_public)
        self.assertFalse(job.is_protected)

    def test_get_job_execution_with_id(self):
        self.mock_response_json_file_values("get_job_execution_response.json")
        job = self.proxy.get_job_execution("any-job-id")
        self.session.get.assert_called_once_with(
            "jobs/any-job-id",
            endpoint_filter=self.service,
            endpoint_override=self.service.get_endpoint_override(),
        )
        self.assertIsInstance(job, _je.JobExecution)
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

    def test_delete_job_execution_binary_with_id(self):
        self.proxy.delete_job_execution("any-job-id")
        self.assert_session_delete("jobs/any-job-id")

    def test_delete_job_execution_binary_with_instance(self):
        self.proxy.delete_job_execution(_je.JobExecution(id="any-job-id"))
        self.assert_session_delete("jobs/any-job-id")
