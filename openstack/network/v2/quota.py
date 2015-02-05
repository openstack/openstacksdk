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


class Quota(resource.Resource):
    resource_key = 'quota'
    resources_key = 'quotas'
    base_path = '/quotas'
    service = network_service.NetworkService()

    # capabilities
    allow_list = True

    # Properties
    floating_ip = resource.prop('floatingip', type=int)
    network = resource.prop('network', type=int)
    port = resource.prop('port', type=int)
    project_id = resource.prop('tenant_id')
    router = resource.prop('router', type=int)
    subnet = resource.prop('subnet', type=int)
