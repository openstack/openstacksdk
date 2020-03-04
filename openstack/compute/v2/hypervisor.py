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


from openstack import resource


class Hypervisor(resource.Resource):
    resource_key = 'hypervisor'
    resources_key = 'hypervisors'
    base_path = '/os-hypervisors'

    # capabilities
    allow_fetch = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'hypervisor_hostname_pattern', 'with_servers'
    )

    # Hypervisor id is a UUID starting with 2.53
    _max_microversion = '2.53'

    # Properties
    #: Status of hypervisor
    status = resource.Body('status')
    #: State of hypervisor
    state = resource.Body('state')
    #: Name of hypervisor
    name = resource.Body('hypervisor_hostname')
    #: Service details
    service_details = resource.Body('service')
    #: Count of the VCPUs in use
    vcpus_used = resource.Body('vcpus_used')
    #: Count of all VCPUs
    vcpus = resource.Body('vcpus')
    #: Count of the running virtual machines
    running_vms = resource.Body('running_vms')
    #: The type of hypervisor
    hypervisor_type = resource.Body('hypervisor_type')
    #: Version of the hypervisor
    hypervisor_version = resource.Body('hypervisor_version')
    #: The amount, in gigabytes, of local storage used
    local_disk_used = resource.Body('local_gb_used')
    #: The amount, in gigabytes, of the local storage device
    local_disk_size = resource.Body('local_gb')
    #: The amount, in gigabytes, of free space on the local storage device
    local_disk_free = resource.Body('free_disk_gb')
    #: The amount, in megabytes, of memory
    memory_used = resource.Body('memory_mb_used')
    #: The amount, in megabytes, of total memory
    memory_size = resource.Body('memory_mb')
    #: The amount, in megabytes, of available memory
    memory_free = resource.Body('free_ram_mb')
    #: Measurement of the hypervisor's current workload
    current_workload = resource.Body('current_workload')
    #: Information about the hypervisor's CPU
    cpu_info = resource.Body('cpu_info')
    #: IP address of the host
    host_ip = resource.Body('host_ip')
    #: Disk space available to the scheduler
    disk_available = resource.Body("disk_available_least")


HypervisorDetail = Hypervisor
