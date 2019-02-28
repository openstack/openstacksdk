# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from openstack import resource


class ProgressDetailsItem(resource.Resource):
    #: The timestamp of recovery workflow task.
    timestamp = resource.Body("timestamp")
    #: The message of recovery workflow task.
    message = resource.Body("message")
    #: The progress of recovery workflow task.
    progress = resource.Body("progress")


class RecoveryWorkflowDetailItem(resource.Resource):
    #: The progress of recovery workflow.
    progress = resource.Body("progress")
    #: The name of recovery workflow.
    name = resource.Body("name")
    #: The state of recovery workflow.
    state = resource.Body("state")
    #: The progress details of this recovery workflow.
    progress_details = resource.Body(
        "progress_details", type=list, list_type=ProgressDetailsItem)


class Notification(resource.Resource):
    resource_key = "notification"
    resources_key = "notifications"
    base_path = "/notifications"

    # capabilities
    # 1] GET /v1/notifications
    # 2] GET /v1/notifications/<notification_uuid>
    # 3] POST /v1/notifications
    allow_list = True
    allow_fetch = True
    allow_create = True
    allow_commit = False
    allow_delete = False

    # Properties
    # Refer "https://github.com/openstack/masakari/tree/
    # master/masakari/api/openstack/ha/schemas/notificaions.py"
    # for properties of notifications API

    #: A ID of representing this notification.
    id = resource.Body("id")
    #: A Uuid of representing this notification.
    notification_uuid = resource.Body("notification_uuid")
    #: A created time of representing this notification.
    created_at = resource.Body("created_at")
    #: A latest updated time of representing this notification.
    updated_at = resource.Body("updated_at")
    #: The type of failure. Valuse values include ''COMPUTE_HOST'',
    #: ''VM'', ''PROCESS''
    type = resource.Body("type")
    #: The hostname of this notification.
    hostname = resource.Body("hostname")
    #: The status for this notitication.
    status = resource.Body("status")
    #: The generated_time for this notitication.
    generated_time = resource.Body("generated_time")
    #: The payload of this notification.
    payload = resource.Body("payload")
    #: The source host uuid of this notification.
    source_host_uuid = resource.Body("source_host_uuid")
    #: The recovery workflow details of this notification.
    recovery_workflow_details = resource.Body(
        "recovery_workflow_details",
        type=list, list_type=RecoveryWorkflowDetailItem)

    _query_mapping = resource.QueryParameters(
        "sort_key", "sort_dir", source_host_uuid="source_host_uuid",
        type="type", status="status", generated_since="generated-since")
