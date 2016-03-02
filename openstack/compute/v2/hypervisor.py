# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from openstack.compute import compute_service
from openstack import resource


class Hypervisor(resource.Resource):

    name_attribute = 'hypervisor_hostname'
    resource_key = 'hypervisor'
    resources_key = 'hypervisors'
    base_path = '/os-hypervisors'

    service = compute_service.ComputeService()

    # capabilities
    allow_retrieve = True
    allow_list = True

    # Properties
    #: status of hypervisor
    status = resource.prop('status')

    #: state of hypervisor
    state = resource.prop('state')

    #: name of hypervisor
    hypervisor_hostname = resource.prop('hypervisor_hostname')
