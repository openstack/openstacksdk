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


class Job(resource.Resource):
    resource_key = "job"
    resources_key = "jobs"
    base_path = "/jobs"
    service = map_reduce_service.MapReduceService()

    # capabilities
    allow_create = True
    allow_update = True
    patch_update = True
    allow_list = True
    allow_get = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        "sort_by"
    )

    #: Properties
    #: Job name
    name = resource.Body("name")
    #: Job type, supports: ``MapReduce``, ``Spark``, ``Hive``, ``hql``,
    #: ``DistCp``, ``SparkScript``, ``SparkSql``
    type = resource.Body("type")
    #: A list of programs to be executed by the job
    mains = resource.Body("mains", type=list)
    #: A list of job-binaries required by the job
    libs = resource.Body("libs", type=list)
    #: Reserved attribute, user customer interfaces
    interface = resource.Body("interface", type=list)
    #: Job description
    description = resource.Body("description")
    #: Reserved attribute, is job protected
    is_protected = resource.Body("is_protected", type=bool)
    #: Reserved attribute, is job public
    is_public = resource.Body("is_public", type=bool)
    #: UTC date and time of the job created time
    created_at = resource.Body("created_at")
    #: UTC date and time of the job last updated time
    updated_at = resource.Body("updated_at")
    #: The tenant this job belongs to
    tenant_id = resource.Body("tenant_id")
