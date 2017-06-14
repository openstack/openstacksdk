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


class Listener(resource.Resource):
    resource_key = 'listeners'
    resources_key = 'listeners'
    base_path = '/elbaas/listeners'
    service = lb_service.LoadBalancerService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_get = True
    allow_delete = True

    # except update_time、create_time、admin_state_up、session_sticky和member_number
    _query_mapping = resource.QueryParameters(
        'loadbalancer_id', 'id', 'name', 'status', 'type', 'bandwidth',
        'vpc_id', 'vip_subnet_id', 'vip_address', 'security_group_id',
        'description',
        is_admin_state_up='admin_state_up'
    )

    #: Properties
    #: The listener name
    name = resource.Body('name')
    #: The listener description
    description = resource.Body('description')
    #: The listener status
    #: Valid values include ``ACTIVE``, ``PENDING_CREATE``, ``ERROR``
    status = resource.Body('status')
    #: The admin state of listener, *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: The server number of the listener
    member_number = resource.Body('member_number')
    #: The health check id of the listener
    healthcheck_id = resource.Body('healthcheck_id')
    #: The listener description
    loadbalancer_id = resource.Body('loadbalancer_id')
    #: The listener protocol, if load-balancer is Internal, UDP is not allowed
    #: Valid values include ``HTTP``, ``HTTPS``, ``TCP``, ``UDP``
    protocol = resource.Body('protocol')
    #: The listener port (1-65535)
    port = resource.Body('port', type=int)
    #: The listener backend port (1-65535)
    backend_port = resource.Body('backend_port', type=int)
    #: The listener backend protocol, if protocol is UDP, only UDP is allowed
    #: Valid values include ``HTTP``, ``TCP``, ``UDP``
    backend_protocol = resource.Body('backend_protocol')
    #: Load balance algorithm of the listener
    #: Valid values include ``roundrobin``, ``leastconn``, ``source``
    lb_algorithm = resource.Body('lb_algorithm')
    #: Is the listener session sticky *Type: bool*
    is_session_sticky = resource.Body('session_sticky', type=bool)
    #: HTTP session sticky type, value should be `insert`. (by default)
    #  only effect when protocol is `HTTP` and is_session_sticky is true.
    sticky_session_type = resource.Body('sticky_session_type')
    #: HTTP cookie timeout, (1-1440) minute
    cookie_timeout = resource.Body('cookie_timeout', type=int)
    #: TCP session timeout, (1-5) minute
    tcp_timeout = resource.Body('tcp_timeout', type=int)
    #: Should TCP keeping connection when server is deleted, *Type: bool*
    is_tcp_draining = resource.Body('tcp_draining', type=bool)
    #: TCP draining timeout, (0-60) minute
    tcp_draining_timeout = resource.Body('tcp_draining_timeout', type=int)
    #: SSL certificate id, required when protocol is HTTPS
    certificate_id = resource.Body('certificate_id')
    #: UDP timeout, (1-1440) minute
    udp_timeout = resource.Body('udp_timeout', type=int)
    #: SSL protocol, TLSv1.2 by default
    #: Valid values include ``TLSv1.2``, ``TLSv1.1``, ``TLSv1``
    ssl_protocols = resource.Body('ssl_protocols')
    #: SSL protocol, TLSv1.2 by default
    #: Valid values include ``Default``, ``Extended``, ``Strict``
    ssl_ciphers = resource.Body('ssl_ciphers')
    #: Timestamp when the listener was created
    created_time = resource.Body('created_time')
    #: Timestamp when the listener was last updated
    updated_time = resource.Body('updated_time')
