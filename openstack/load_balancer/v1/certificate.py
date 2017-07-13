# -*- coding: utf-8 -*-
#
# Copyright 2017 HuaWei Tld
#
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

from openstack.load_balancer import load_balancer_service as lb_service
from openstack import resource2 as resource


class Certificate(resource.Resource):
    resources_key = 'certificates'
    base_path = '/elbaas/certificate'
    service = lb_service.LoadBalancerService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_delete = True
    allow_update = True

    _query_mapping = resource.QueryParameters(
    )

    #: Properties
    #: The listener name
    name = resource.Body('name')
    description = resource.Body('description')
    certificate = resource.Body('certificate')
    private_key = resource.Body('private_key')
    create_time = resource.Body('create_time')
    update_time = resource.Body('update_time')
