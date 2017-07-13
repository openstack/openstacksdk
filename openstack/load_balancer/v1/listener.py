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
from openstack import resource2 as resource
from openstack import utils
from openstack.load_balancer import load_balancer_service as lb_service


class Listener(resource.Resource):
    base_path = "/elbaas/listeners"
    service = lb_service.LoadBalancerService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_get = True
    allow_delete = True
    allow_update = True

    _query_mapping = resource.QueryParameters(
        "id",
        "name",
        "loadbalancer_id",
        "description",
        "status",
        "healthcheck_id",
        "certificate_id",
        "port",
        "protocol",
        "backend_port",
        "backend_protocol",
        "sticky_session_type",
        "lb_algorithm",
        "cookie_timeout",
        "tcp_timeout",
        "udp_timeout",
        "ssl_protocols",
        "ssl_ciphers"
    )

    #: Properties
    #: The listener name
    name = resource.Body("name")
    #: The listener description
    description = resource.Body("description")
    #: The listener status
    #: Valid values include ``ACTIVE``, ``PENDING_CREATE``, ``ERROR``
    status = resource.Body("status")
    #: The admin state of listener, *Type: bool*
    is_admin_state_up = resource.Body("admin_state_up", type=bool)
    #: The server amount of the listener
    member_number = resource.Body("member_number")
    #: The health check reference of the listener
    healthcheck_id = resource.Body("healthcheck_id")
    #: The load balancer reference of the listener
    loadbalancer_id = resource.Body("loadbalancer_id")
    #: The port to be monitored (1-65535)
    port = resource.Body("port", type=int)
    #: The protocol to be monitored, if load balancer type is Internal,
    #: UDP protocol is not allowed.
    #: Valid values include ``HTTP``, ``HTTPS``, ``TCP``, ``UDP``
    protocol = resource.Body("protocol")
    #: The port of backend server to be monitored (1-65535)
    backend_port = resource.Body("backend_port", type=int)
    #: The backend protocol to be monitored, if protocol is UDP,
    #: only UDP is allowed for backend protocol.
    #: Valid values include ``HTTP``, ``TCP``, ``UDP``
    backend_protocol = resource.Body("backend_protocol")
    #: Load balance algorithm of the listener.
    #: Valid values include ``roundrobin``, ``leastconn``, ``source``
    lb_algorithm = resource.Body("lb_algorithm")
    #: Should stick session,  *Type: bool*
    is_session_sticky = resource.Body("session_sticky", type=bool)
    #: HTTP session sticky type, value should be `insert`. (by default)
    #  only effect when protocol is `HTTP` and is_session_sticky is true.
    sticky_session_type = resource.Body("sticky_session_type")
    #: HTTP cookie timeout, (1-1440) minute
    cookie_timeout = resource.Body("cookie_timeout", type=int)
    #: TCP session timeout, (1-5) minute
    tcp_timeout = resource.Body("tcp_timeout", type=int)
    #: Should TCP keeping connection when server is deleted, *Type: bool*
    is_tcp_draining = resource.Body("tcp_draining", type=bool)
    #: TCP draining timeout, (0-60) minute
    tcp_draining_timeout = resource.Body("tcp_draining_timeout", type=int)
    #: SSL certificate id, required when protocol is HTTPS
    certificate_id = resource.Body("certificate_id")
    #: UDP timeout, (1-1440) minute
    udp_timeout = resource.Body("udp_timeout", type=int)
    #: SSL protocol, TLSv1.2 by default, only effects when protocol is HTTPS
    #: Valid values include ``TLSv1.2``, ``TLSv1.1``, ``TLSv1``
    ssl_protocols = resource.Body("ssl_protocols")
    #: SSL protocol, TLSv1.2 by default, only effects when protocol is HTTPS
    #: Valid values include ``Default``, ``Extended``, ``Strict``
    ssl_ciphers = resource.Body("ssl_ciphers")
    #: Timestamp when the listener was created
    create_time = resource.Body("create_time")
    #: Timestamp when the listener was last updated
    update_time = resource.Body("update_time")

    def add_members(self, session, members):
        """Add backend members

        :param session: openstack session
        :param members: list of dicts which contain the server_id and address.
            server_id is ECS service id, address is ECS server internal IP.
            [{"server_id": "dbecb618-2259-405f-ab17-9b68c4f541b0",
              "address": "172.16.0.31"}] for example.
        :return: a sync OperateMemberJob
        :rtype: :class:`~openstack.load_balancer.v1.member.OperateMemberJob`
        """
        url = utils.urljoin(self.base_path, self.id, "members")
        endpoint_override = self.service.get_endpoint_override()
        response = session.post(url,
                                endpoint_filter=self.service,
                                endpoint_override=endpoint_override,
                                json=members,
                                headers={})

        job = OperateMemberJob()
        job._translate_response(response)
        return job

    def remove_members(self, session, members):
        """Add backend members

        :param session: openstack session
        :param members: member list to be removed from listener,
            list of members (ECS server id) belongs to the listener
            ["dbecb618-2259-405f-ab17-9b68c4f541b0"] for example.
        :return: a sync OperateMemberJob
        :rtype: :class:`~openstack.load_balancer.v1.member.OperateMemberJob`
        """
        url = utils.urljoin(self.base_path, self.id, "members/action")
        endpoint_override = self.service.get_endpoint_override()
        json_body = {"removeMember": [dict(id=mid) for mid in members]}
        response = session.post(url,
                                endpoint_filter=self.service,
                                endpoint_override=endpoint_override,
                                json=json_body,
                                headers={})
        job = OperateMemberJob()
        job._translate_response(response)
        return job


class OperateMemberJob(resource.Resource):
    #: Job Id
    id = resource.Body("job_id")
    #: Job uri
    uri = resource.Body("uri")


class Member(resource.Resource):
    base_path = '/elbaas/listeners/%(listener_id)s/members'
    service = lb_service.LoadBalancerService()

    # capabilities
    allow_create = True
    allow_delete = True
    allow_list = True

    #: Properties
    #: Load balancer listener reference of this member
    listener_id = resource.URI("listener_id")
    #: EIP address of the member server
    address = resource.Body('address')
    #: internal IP address of the member server
    server_address = resource.Body('server_address')
    #: member server ID
    server_id = resource.Body('server_id')
    #: member server name
    server_name = resource.Body('server_name')
    #: member server status, valid value includes: ``ACTIVE``, ``PENDING``,
    #: ``ERROR``
    status = resource.Body('status')
    #: Health check status, valid value includes: ``NORMAL``, ``ABNORMAL``,
    #: ``UNAVAILABLE``
    health_status = resource.Body('health_status')
    #: List of listeners associated with this member.
    #: *Type: list of dicts which contain the listener IDs*
    listeners = resource.Body('listeners', type=list)
    #: UTC date and time of the member created time
    create_time = resource.Body("create_time")
    #: UTC date and time of the member updated time
    update_time = resource.Body("update_time")
