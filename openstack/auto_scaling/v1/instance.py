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
from openstack.auto_scaling import auto_scaling_service


class Instance(resource.Resource):
    resource_key = 'scaling_group_instance'
    resources_key = 'scaling_group_instances'
    base_path = '/scaling_group_instance'
    query_marker_key = 'start_number'
    next_marker_path = 'start_number'
    service = auto_scaling_service.AutoScalingService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_get = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        "scaling_group_id", "health_status", "limit",
        lifecycle_status="life_cycle_state",
        marker=query_marker_key
    )

    #: Properties
    #: Valid values include ``private``, ``public``
    #: AutoScaling instance id
    id = resource.Body('instance_id')
    #: AutoScaling instance name
    name = resource.Body('instance_name')
    #: Id of AutoScaling group the instance belongs to
    scaling_group_id = resource.Body('scaling_group_id')
    #: Name of AutoScaling group the instance belongs to
    scaling_group_name = resource.Body('scaling_group_name')
    #: Id of AutoScaling config the instance create with
    scaling_configuration_id = resource.Body('scaling_configuration_id')
    #: Name of AutoScaling config the instance create with
    scaling_configuration_name = resource.Body('scaling_configuration_name')
    #: AutoScaling instance lifecycle state, valid values include:
    #: ``INSERVICE``, ``PENDING``, ``REMOVING``
    lifecycle_state = resource.Body('life_cycle_state')
    #: AutoScaling instance health state, valid values include:
    #: ``INITIALIZING``, ``NORMAL``, ``ERROR``
    health_status = resource.Body('health_status')
    #: AutoScaling instance create time
    create_time = resource.Body('create_time')

    def batch_remove(self, session, instances, delete_instance=False):
        """ batch remove auto-scaling instances

        make sure all configs should not been used by auto-scaling group
        :param session: openstack session
        :param list instances: The list item value can be the ID of an instance
            or a :class:`~openstack.auto_scaling.v2.instance.Instance` instance
        :param bool delete_instance: When set to ``True``, instance will be
                deleted after removed
        :return:
        """
        ids = [instance.id if isinstance(instance, Instance) else instance
               for instance in instances]
        json_body = {
            "action": "REMOVE",
            "instances_id": ids,
            "instance_delete": "yes" if delete_instance else "no"
        }
        endpoint_override = self.service.get_endpoint_override()
        uri = utils.urljoin("/scaling_group_instance",
                            self.scaling_group_id,
                            "action")
        return session.post(uri,
                            headers={"Accept": "*"},
                            endpoint_filter=self.service,
                            endpoint_override=endpoint_override,
                            json=json_body)

    def batch_add(self, session, instances):
        """ batch remove auto-scaling instances

        make sure all configs should not been used by auto-scaling group
        :param session: openstack session
        :param list instances: The list item value can be the ID of an instance
            or a :class:`~openstack.auto_scaling.v2.instance.Instance` instance
        :return:
        """
        ids = [instance.id if isinstance(instance, Instance) else instance
               for instance in instances]
        json_body = {
            "action": "ADD",
            "instances_id": ids
        }
        endpoint_override = self.service.get_endpoint_override()
        uri = utils.urljoin("/scaling_group_instance",
                            self.scaling_group_id,
                            "action")
        return session.post(uri,
                            headers={"Accept": "*"},
                            endpoint_filter=self.service,
                            endpoint_override=endpoint_override,
                            json=json_body)