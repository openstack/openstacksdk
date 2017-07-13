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
from openstack.cloud_eye import cloud_eye_service
from openstack.cloud_eye.v1.metric import Metric
from openstack import resource2 as resource
from openstack import utils


class Alarm(resource.Resource):
    """CloudEye alarm resource"""
    resource_key = 'metric_alarms'
    resources_key = 'metric_alarms'
    base_path = '/alarms'
    next_marker_path = 'meta_data.marker'
    query_marker_key = 'start'
    service = cloud_eye_service.CloudEyeService()

    # capabilities
    allow_list = True
    allow_get = True
    allow_delete = True

    _query_mapping = resource.QueryParameters(
        "order", "limit",
        marker=query_marker_key
    )

    #: Properties
    #: ID of the Alarm
    id = resource.Body('alarm_id')
    #: Alarm name
    name = resource.Body('alarm_name')
    #: Alarm description
    description = resource.Body('alarm_description')
    #: The metric of the alarm
    metric = resource.Body('metric', type=Metric)
    #: Is Alarm enabled
    alarm_enabled = resource.Body('alarm_enabled', type=bool)
    #: Is Alarm actions enabled
    alarm_action_enabled = resource.Body('alarm_action_enabled', type=bool)
    #: Alarm status
    #: valid values include: ``ok``, ``alarm``, ``insufficient_data``
    state = resource.Body('alarm_state')
    #: Last update time
    update_time = resource.Body('update_time')
    #: Alarm trigger condition
    condition = resource.Body('condition', type=dict)
    #: Alarm trigger action
    alarm_actions = resource.Body('alarm_actions', type=list)
    #: Alarm dismissing trigger action
    ok_actions = resource.Body('ok_actions', type=list)
    #: Insufficient data trigger actions
    insufficientdata_actions = resource.Body('insufficientdata_actions',
                                             type=list)

    def _action(self, session, body):
        """Preform alarm actions given the message body."""
        url = utils.urljoin(self.base_path, self.id, 'action')
        endpoint_override = self.service.get_endpoint_override()
        return session.put(url,
                           endpoint_filter=self.service,
                           endpoint_override=endpoint_override,
                           json=body,
                           headers={})

    def enable(self, session):
        """Enable alarm"""
        body = {'alarm_enabled': True}
        self._action(session, body)

    def disable(self, session):
        """Enable alarm"""
        body = {'alarm_enabled': False}
        self._action(session, body)
