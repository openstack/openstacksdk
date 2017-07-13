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
from openstack.map_reduce import map_reduce_service
from openstack import resource2 as resource
from openstack import utils


class JobExecution(resource.Resource):
    """Map Reduce Job Execution Resource"""
    resource_key = "job_execution"
    resources_key = "job_executions"
    base_path = "/job-executions"
    service = map_reduce_service.MapReduceService()

    # capabilities
    allow_list = True
    allow_get = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        "sort_by"
    )

    #: Properties
    #: A dict contains job running information returned by Oozie
    info = resource.Body("info", type=dict)
    #: The cluster which executed the job
    cluster_id = resource.Body("cluster_id")
    #: The job reference been executed
    job_id = resource.Body("job_id")
    #: Workflow ID of Oozie
    engine_job_id = resource.Body("engine_job_id")
    #: Workflow ID returned by Oozie
    oozie_job_id = resource.Body("oozie_job_id")
    #: Response code of job execution
    return_code = resource.Body("return_code")
    #: Input data reference(ID) of the job execution
    input_id = resource.Body("input_id")
    #: Output data reference(ID) of the job execution
    output_id = resource.Body("output_id")
    #: Job execution configurations
    job_configs = resource.Body("job_configs", type=dict)
    #: Input Data source dict of the job execution, key is input id and value
    #: is the input URL
    data_source_urls = resource.Body("data_source_urls")
    #: Reserved attribute, is job binary protected
    is_protected = resource.Body("is_protected", type=bool)
    #: Reserved attribute, is job binary public
    is_public = resource.Body("is_public", type=bool)
    #: UTC date and time of the job-execution start time
    start_time = resource.Body("start_time")
    #: UTC date and time of the job-execution end time
    end_time = resource.Body("end_time")
    #: UTC date and time of the job-execution created time
    created_at = resource.Body("created_at")
    #: UTC date and time of the job-execution last updated time
    updated_at = resource.Body("updated_at")
    #: The tenant this job-execution belongs to
    tenant_id = resource.Body("tenant_id")

    def cancel(self, session):
        """cancel self's execution

        :param session: openstack session
        :return:
        """
        uri = utils.urljoin(self.base_path, self.id, 'cancel')
        endpoint_override = self.service.get_endpoint_override()
        response = session.get(uri,
                               endpoint_filter=self.service,
                               endpoint_override=endpoint_override)
        self._translate_response(response)
        return self

    def create(self, session):
        """create a job execution and execute it

        :param session: openstack session
        :return:
        """
        uri = utils.urljoin("/jobs", self.job_id, '/execute')
        endpoint_override = self.service.get_endpoint_override()
        body = self._body.dirty
        response = session.post(uri,
                                headers={"Accept": "application/json"},
                                endpoint_filter=self.service,
                                endpoint_override=endpoint_override,
                                json=body)
        self._translate_response(response)
        return self
