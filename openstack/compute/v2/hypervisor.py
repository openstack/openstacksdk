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
from openstack import resource2


class Hypervisor(resource2.Resource):
    resource_key = 'hypervisor'
    resources_key = 'hypervisors'
    base_path = '/os-hypervisors'

    service = compute_service.ComputeService()

    # capabilities
    allow_get = True
    allow_list = True

    # Properties
    #: Status of hypervisor
    status = resource2.Body('status')
    #: State of hypervisor
    state = resource2.Body('state')
    #: Name of hypervisor
    name = resource2.Body('hypervisor_hostname')
    #: Service details
    service_details = resource2.Body('service')
    #: Count of the VCPUs in use
    vcpus_used = resource2.Body('vcpus_used')
    #: Count of all VCPUs
    vcpus = resource2.Body('vcpus')
    #: Count of the running virtual machines
    running_vms = resource2.Body('running_vms')
    #: The type of hypervisor
    hypervisor_type = resource2.Body('hypervisor_type')
    #: Version of the hypervisor
    hypervisor_version = resource2.Body('hypervisor_version')
    #: The amount, in gigabytes, of local storage used
    local_disk_used = resource2.Body('local_gb_used')
    #: The amount, in gigabytes, of the local storage device
    local_disk_size = resource2.Body('local_gb')
    #: The amount, in gigabytes, of free space on the local storage device
    local_disk_free = resource2.Body('free_disk_gb')
    #: The amount, in megabytes, of memory
    memory_used = resource2.Body('memory_mb_used')
    #: The amount, in megabytes, of total memory
    memory_size = resource2.Body('memory_mb')
    #: The amount, in megabytes, of available memory
    memory_free = resource2.Body('free_ram_mb')
    #: Measurement of the hypervisor's current workload
    current_workload = resource2.Body('current_workload')
    #: Information about the hypervisor's CPU
    cpu_info = resource2.Body('cpu_info')
    #: IP address of the host
    host_ip = resource2.Body('host_ip')
    #: Disk space available to the scheduler
    disk_available = resource2.Body("disk_available_least")
