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


class ScheduledPolicy(resource.Resource):
    #: schedule time,
    #:  ** if policy type is ``SCHEDULED``, launch time should be
    #:          ``YYYY-MM-DDThh:mmZ``,
    #:  ** if policy type is ``RECURRENCE``, launch time should be ``hh:mm``
    launch_time = resource.Body('launch_time')
    #: Recurrence Type,
    #: valid values include: ``Daily``, ``Weekly``, ``Monthly``
    recurrence_type = resource.Body('recurrence_type')
    #: Used in concert with ``recurrence_type``,
    #:  ** if recurrence_type is Daily, recurrence_value has no meaning
    #:  ** if recurrence_type is Weekly, recurrence_value means days of week,
    #:       1,3,5 means scheduled at monday, Wednesday, Friday of every week
    #:  ** if recurrence_type is Monthly, recurrence_value means days of month
    #:       1,10,30 means scheduled at first, 10th, 30th day of every month
    recurrence_value = resource.Body('recurrence_value')
    #: policy effect start time (UTC)
    start_time = resource.Body('start_time')
    #: policy effect end time (UTC)
    end_time = resource.Body('end_time')


class Action(resource.Resource):
    #: Scaling trigger action type
    #: valid values include: ``ADD``, ``REMOVE``, ``SET``
    operation = resource.Body('operation')
    #: The instance number action for
    instance_number = resource.Body('instance_number')


class Policy(resource.Resource):
    """AutoScaling Policy Resource"""
    resource_key = 'scaling_policy'
    resources_key = 'scaling_policies'
    base_path = '/scaling_policy'
    query_marker_key = 'start_number'
    service = auto_scaling_service.AutoScalingService()

    # capabilities
    allow_create = True
    allow_list = True
    allow_get = True
    allow_delete = True
    allow_update = True

    _query_mapping = resource.QueryParameters(
        'scaling_group_id', 'limit',
        name='scaling_policy_name',
        type='scaling_policy_type',
        marker=query_marker_key
    )

    #: Properties
    #: AutoScaling policy ID
    id = resource.Body('scaling_policy_id')
    #: AutoScaling policy name
    name = resource.Body('scaling_policy_name')
    #: AutoScaling policy trigger type
    #: valid values include: ``ALARM``, ``SCHEDULED``, ``RECURRENCE``
    type = resource.Body('scaling_policy_type')
    #: AutoScaling group reference the policy apply to
    scaling_group_id = resource.Body('scaling_group_id')
    alarm_id = resource.Body('alarm_id')
    scheduled_policy = resource.Body('scheduled_policy',
                                     type=ScheduledPolicy,
                                     default={})
    scaling_policy_action = resource.Body('scaling_policy_action',
                                          type=Action,
                                          default={})
    cool_down_time = resource.Body('cool_down_time')
    create_time = resource.Body('create_time')
    #: valid values include: ``INSERVICE``, ``PAUSED``
    status = resource.Body('policy_status')

    @classmethod
    def get_next_marker(cls, response_json, yielded, query_params):
        from openstack.auto_scaling.v1 import get_next_marker
        return get_next_marker(response_json, yielded)

    @classmethod
    def get_list_uri(cls, params):
        return "/scaling_policy/%(scaling_group_id)s/list" % params

    def _action(self, session, body):
        """Preform alarm actions given the message body."""
        url = utils.urljoin(self.base_path, self.id, "action")
        endpoint_override = self.service.get_endpoint_override()
        return session.post(url,
                            endpoint_filter=self.service,
                            endpoint_override=endpoint_override,
                            json=body,
                            headers={})

    def execute(self, session):
        """execute policy"""
        body = {"action": "execute"}
        self._action(session, body)

    def pause(self, session):
        """pause policy"""
        body = {"action": "pause"}
        self._action(session, body)

    def resume(self, session):
        """resume policy"""
        body = {"action": "resume"}
        self._action(session, body)
