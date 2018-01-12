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

from openstack.network import network_service
from openstack import resource


class MeteringLabelRule(resource.Resource):
    resource_key = 'metering_label_rule'
    resources_key = 'metering_label_rules'
    base_path = '/metering/metering-label-rules'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'direction', 'metering_label_id', 'remote_ip_prefix',
        project_id='tenant_id',
    )

    # Properties
    #: ingress or egress: The direction in which metering label rule is
    #: applied. Default: ``"ingress"``
    direction = resource.Body('direction')
    #: Specify whether the ``remote_ip_prefix`` will be excluded or not
    #: from traffic counters of the metering label, ie: to not count the
    #: traffic of a specific IP address of a range. Default: ``False``,
    #: *Type: bool*
    is_excluded = resource.Body('excluded', type=bool)
    #: The metering label ID to associate with this metering label rule.
    metering_label_id = resource.Body('metering_label_id')
    #: The ID of the project this metering label rule is associated with.
    project_id = resource.Body('tenant_id')
    #: The remote IP prefix to be associated with this metering label rule.
    remote_ip_prefix = resource.Body('remote_ip_prefix')
