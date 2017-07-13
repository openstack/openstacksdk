#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
from openstack import resource2 as resource
from openstack.resource2 import QueryParameters
from openstack.volume_backup import volume_backup_service


class BackupTask(resource.Resource):
    """Cloud Backup"""
    resources_key = "tasks"
    base_path = "/backuppolicy/%(policy_id)s/backuptasks"
    service = volume_backup_service.VolumeBackupService()

    # capabilities
    allow_list = True

    _query_mapping = QueryParameters("sort_dir", "sort_key", "status",
                                     "limit", "marker", "offset", "status",
                                     id="job_id")

    #: Properties
    #: Task job id
    id = resource.Body("job_id")
    #: Name of backup created by this task name
    backup_name = resource.Body("backup_name")
    #: Resource ID (volume-id for example)
    resource_id = resource.Body("resource_id")
    #: Resource Type (volume for example)
    resource_type = resource.Body("resource_type")
    #: Task status, valid values include: ``RUNNING``, ``EXECUTE_TIMEOUT``,
    #: ``WAITING``, EXECUTE_FAIL``, ``EXECUTE_SUCCESS``
    status = resource.Body("status")
    #: task created at
    created_at = resource.Body("created_at")
    #: task finished at
    finished_at = resource.Body("finished_at")
