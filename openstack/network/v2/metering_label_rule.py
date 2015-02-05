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
    base_path = '/metering-label-rules'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True
    put_update = True

    # Properties
    direction = resource.prop('direction')
    excluded = resource.prop('excluded', type=bool)
    metering_label_id = resource.prop('metering_label_id')
    remote_ip_prefix = resource.prop('remote_ip_prefix')
