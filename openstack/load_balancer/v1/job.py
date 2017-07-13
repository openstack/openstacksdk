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
from openstack.load_balancer import load_balancer_service as lb_service
from openstack import resource2 as resource


class Job(resource.Resource):
    """Job Resource"""
    base_path = "/jobs"
    service = lb_service.LoadBalancerService()

    # capabilities
    allow_get = True

    #: Properties
    id = resource.Body("job_id")
    type = resource.Body("job_type")
    begin_time = resource.Body("begin_time")
    end_time = resource.Body("end_time")
    entities = resource.Body("entities")
    status = resource.Body("status")
    error_code = resource.Body("error_code")
    fail_reason = resource.Body("fail_reason")
