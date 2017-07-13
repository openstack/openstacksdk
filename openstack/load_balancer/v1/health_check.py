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


class HealthCheck(resource.Resource):
    base_path = '/elbaas/healthcheck'
    service = lb_service.LoadBalancerService()

    # capabilities
    allow_create = True
    allow_delete = True
    allow_update = True
    allow_get = True

    #: Properties
    #: The health check name
    name = resource.Body('name')
    #: The Load balancer listener to be checked
    listener_id = resource.Body('listener_id')
    #: The health check protocol, valid values include: ``TCP``, ``HTTP``
    healthcheck_protocol = resource.Body('healthcheck_protocol')
    #: The health check connect port (1-65535)
    healthcheck_connect_port = resource.Body('healthcheck_connect_port')
    #: The health check URI, effects when protocol is HTTP
    healthcheck_uri = resource.Body('healthcheck_uri')
    #: The max interval between two health check, (1-5) seconds
    healthcheck_interval = resource.Body('healthcheck_interval')
    #: The health check request timeout (1-50) seconds
    healthcheck_timeout = resource.Body('healthcheck_timeout')
    #: The threshold of success checking for turning fail to success
    healthy_threshold = resource.Body('healthy_threshold')
    #: The threshold of failed checking for turning success to fail
    unhealthy_threshold = resource.Body('unhealthy_threshold')
    #: UTC date and time of health check been created
    create_time = resource.Body('create_time')
    #: UTC date and time of health check been updated
    update_time = resource.Body('update_time')
