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
from openstack.volume_backup import volume_backup_service


class Job(resource.Resource):
    """Volume backup Job Resource"""
    base_path = "/jobs"
    service = volume_backup_service.VolumeBackupService()

    # capabilities
    allow_list = True

    #: Properties
    id = resource.Body("job_id")
    type = resource.Body("job_type")
    begin_time = resource.Body("begin_time")
    end_time = resource.Body("end_time")
    entities = resource.Body("entities")
    status = resource.Body("status")
    error_code = resource.Body("error_code")
    fail_reason = resource.Body("fail_reason")
    message = resource.Body("message")
    code = resource.Body("code")
    sub_jobs = resource.Body("sub_jobs")
