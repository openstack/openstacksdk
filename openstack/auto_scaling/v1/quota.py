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
from openstack.auto_scaling import auto_scaling_service
from openstack import resource2 as resource


class Quota(resource.Resource):
    """AutoScaling Quota resource"""
    resource_key = "quotas.resources"
    resources_key = "quotas.resources"
    base_path = "/quotas"
    service = auto_scaling_service.AutoScalingService()

    # capabilities
    allow_list = True

    #: Properties
    #: Quota of type, current only ``alarm`` is valid
    type = resource.Body("type")
    #: Quota amount has been used
    used = resource.Body("used")
    #: Quota max amount
    max = resource.Body("max")
    #: Quota amount
    quota = resource.Body("quota")


class ScalingQuota(Quota):
    base_path = "/quotas/%(scaling_group_id)s"

    _query_mapping = resource.QueryParameters(
        "scaling_group_id"
    )
