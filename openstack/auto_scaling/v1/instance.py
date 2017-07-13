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


class Instance(resource.Resource):
    resource_key = 'scaling_group_instance'
    resources_key = 'scaling_group_instances'
    # ok, we just fix the base path to list because there are no common rules
    # for the operations for instance
    base_path = '/scaling_group_instance/%(scaling_group_id)s/list'
    query_marker_key = 'start_number'
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
    #: AutoScaling instance id
    id = resource.Body('instance_id')
    #: AutoScaling instance name
    name = resource.Body('instance_name')
    #: Id of AutoScaling group the instance belongs to
    scaling_group_id = resource.URI('scaling_group_id')
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

    @classmethod
    def get_next_marker(cls, response_json, yielded, query_params):
        from openstack.auto_scaling.v1 import get_next_marker
        return get_next_marker(response_json, yielded)

    def remove(self, session, delete_instance=False, ignore_missing=True):
        """Remove an instance of auto scaling group

        precondition:
        * the instance must in ``INSERVICE`` status
        * after remove the instance number of auto scaling group should not
           be less than min instance number
        * The owner auto scaling group should not in scaling status
        :param session: openstack session
        :param bool delete_instance: When set to ``True``, instance will be
               deleted after removed
        :param bool ignore_missing: When set to ``False``
           :class:`~openstack.exceptions.ResourceNotFound` will be raised when
           the config does not exist.
           When set to ``True``, no exception will be set when attempting to
           delete a nonexistent config.
        :return:
       """
        uri = utils.urljoin("/scaling_group_instance", self.id)
        endpoint_override = self.service.get_endpoint_override()
        delete_instance = "yes" if delete_instance else "no"
        return session.delete(uri, endpoint_filter=self.service,
                              endpoint_override=endpoint_override,
                              headers={"Accept": ""},
                              params={"instance_delete": delete_instance})

    def batch_remove(self, session, instances, delete_instance=False):
        """batch remove auto-scaling instances

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
        """batch remove auto-scaling instances

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
