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

from openstack import resource


class ResourceLock(resource.Resource):
    resource_key = "resource_lock"
    resources_key = "resource_locks"
    base_path = "/resource-locks"

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_head = False

    _query_mapping = resource.QueryParameters(
        "project_id",
        "created_since",
        "created_before",
        "limit",
        "offset",
        "id",
        "resource_id",
        "resource_type",
        "resource_action",
        "user_id",
        "lock_context",
        "lock_reason",
        "lock_reason~",
        "sort_key",
        "sort_dir",
        "with_count",
        "all_projects",
    )
    # The resource was introduced in this microversion, so it is the minimum
    # version to use it. Openstacksdk currently doesn't allow to set
    # minimum microversions.
    _max_microversion = '2.81'

    #: Properties
    #: The date and time stamp when the resource was created within the
    #: service’s database.
    created_at = resource.Body("created_at", type=str)
    #: The date and time stamp when the resource was last modified within the
    #: service’s database.
    updated_at = resource.Body("updated_at", type=str)
    #: The ID of the user that owns the lock
    user_id = resource.Body("user_id", type=str)
    #: The ID of the project that owns the lock.
    project_id = resource.Body("project_id", type=str)
    #: The type of the resource that is locked, i.e.: share, access rule.
    resource_type = resource.Body("resource_type", type=str)
    #: The UUID of the resource that is locked.
    resource_id = resource.Body("resource_id", type=str)
    #: What action is currently locked, i.e.: deletion, visibility of fields.
    resource_action = resource.Body("resource_action", type=str)
    #: The reason specified while the lock was being placed.
    lock_reason = resource.Body("lock_reason", type=str)
    #: The context that placed the lock (user, admin or service).
    lock_context = resource.Body("lock_context", type=str)
