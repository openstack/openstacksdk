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
from openstack.auto_scaling import auto_scaling_service
from openstack import resource2 as resource
from openstack import utils


class Group(resource.Resource):
    resource_key = "scaling_group"
    resources_key = "scaling_groups"
    base_path = "/scaling_group"
    query_marker_key = "start_number"
    service = auto_scaling_service.AutoScalingService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_get = True
    allow_delete = True
    allow_update = True

    _query_mapping = resource.QueryParameters(
        "scaling_configuration_id", "limit",
        name="scaling_group_name",
        status="scaling_group_status",
        marker=query_marker_key
    )

    #: Properties
    #: AutoScaling group ID
    id = resource.Body("scaling_group_id")
    #: AutoScaling group name
    name = resource.Body("scaling_group_name")
    #: AutoScaling group status,
    #: valid valus includes: ``INSERVICE``, ``PAUSED``, ``ERROR``
    status = resource.Body("scaling_group_status")
    #: AutoScaling group scaling status, *Type: bool*
    is_scaling = resource.Body("is_scaling", type=bool)
    #: AutoScaling group detail
    detail = resource.Body("detail")
    #: VPC id - (Router Id)
    vpc_id = resource.Body("vpc_id")
    #: network id list - (Subnet)
    networks = resource.Body("networks", type=list)
    #: security group id list
    security_groups = resource.Body("security_groups", type=list)
    #: Auto Scaling Config ID reference, used for creating instance
    scaling_configuration_id = resource.Body("scaling_configuration_id")
    #: Auto Scaling Config name
    scaling_configuration_name = resource.Body("scaling_configuration_name")
    #: Current alive instance number
    current_instance_number = resource.Body("current_instance_number")
    #: Desire alive instance number
    desire_instance_number = resource.Body("desire_instance_number")
    #: min alive instance number
    min_instance_number = resource.Body("min_instance_number")
    #: max alive instance number
    max_instance_number = resource.Body("max_instance_number")
    #: CoolDown time, only work with `ALARM` policy.
    #: default is 900, valid range is 0-86400
    cool_down_time = resource.Body("cool_down_time")
    #: load balancer listener id reference
    lb_listener_id = resource.Body("lb_listener_id")
    #: Health periodic audit method, Valid values includes: ``ELB_AUDIT``,
    #: ``NOVA_AUDIT``, ELB_AUDIT and lb_listener_id are used in pairs.
    health_periodic_audit_method = resource.Body(
        "health_periodic_audit_method")
    #: Health periodic audit time, valid values includes: ``5``, ``15``,
    #: ``60``, ``180``, default is ``5`` minutes
    health_periodic_audit_time = resource.Body("health_periodic_audit_time")
    #: Instance terminate policy, valid values includes:
    #: ``OLD_CONFIG_OLD_INSTANCE`` (default), ``OLD_CONFIG_NEW_INSTANCE``,
    #: ``OLD_INSTANCE``, ``NEW_INSTANCE``
    instance_terminate_policy = resource.Body("instance_terminate_policy")
    #: notification methods, ``EMAIL``
    notifications = resource.Body("notifications")
    #: Should delete public ip when terminate instance, default ``false``
    delete_publicip = resource.Body("delete_publicip", type=bool)
    #: availability zones
    availability_zones = resource.Body("available_zones")
    #: Create time of the group
    create_time = resource.Body("create_time")

    @classmethod
    def get_next_marker(cls, response_json, yielded, query_params):
        from openstack.auto_scaling.v1 import get_next_marker
        return get_next_marker(response_json, yielded)

    def _action(self, session, body):
        """Preform group actions given the message body."""
        url = utils.urljoin(self.base_path, self.id, "action")
        endpoint_override = self.service.get_endpoint_override()
        return session.post(url,
                            endpoint_filter=self.service,
                            endpoint_override=endpoint_override,
                            json=body,
                            headers={})

    def resume(self, session):
        """resume group"""
        body = {"action": "resume"}
        self._action(session, body)

    def pause(self, session):
        """pause group"""
        body = {"action": "pause"}
        self._action(session, body)
