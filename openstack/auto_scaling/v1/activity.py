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
from openstack.auto_scaling import auto_scaling_service
from openstack import resource2 as resource


class Activity(resource.Resource):
    resource_key = "scaling_activity_log"
    resources_key = "scaling_activity_log"
    base_path = "/scaling_activity_log/%(scaling_group_id)s"
    query_marker_key = "start_number"
    service = auto_scaling_service.AutoScalingService()

    # capabilities
    allow_list = True

    _query_mapping = resource.QueryParameters(
        "scaling_group_id", "start_time", "end_time", "limit",
        marker=query_marker_key
    )

    #: Properties
    #: AutoScaling Group Reference this activity belongs to
    scaling_group_id = resource.URI("scaling_group_id")
    #: AutoScaling Activity status
    #: valid values include: ``SUCCESS``, ``FAIL``, ``DOING``
    status = resource.Body("status")
    #: UTC date and time of activity begin
    start_time = resource.Body("start_time")
    #: UTC date and time of activity finish
    end_time = resource.Body("end_time")
    #: AutoScaling Activity description
    description = resource.Body("description")
    #: changed instance number during the AutoScaling Activity
    scaling_value = resource.Body("scaling_value")
    #: current instance number during the AutoScaling Activity
    instance_value = resource.Body("instance_value")
    #: desired instance number of the AutoScaling Activity
    desire_value = resource.Body("desire_value")
    #: The instance list removed in the AutoScaling Activity
    instance_removed_list = resource.Body("instance_removed_list")
    #: The instance list deleted in the AutoScaling Activity
    instance_deleted_list = resource.Body("instance_deleted_list")
    #: The instance list added in the AutoScaling Activity
    instance_added_list = resource.Body("instance_added_list")

    @classmethod
    def get_next_marker(cls, response_json, yielded, query_params):
        from openstack.auto_scaling.v1 import get_next_marker
        return get_next_marker(response_json, yielded)
