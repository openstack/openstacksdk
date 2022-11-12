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

from openstack import resource


class ServerDiagnostics(resource.Resource):
    resource_key = 'diagnostics'
    base_path = '/servers/%(server_id)s/diagnostics'

    # capabilities
    allow_fetch = True

    requires_id = False

    _max_microversion = '2.48'

    #: Indicates whether or not a config drive was used for this server.
    has_config_drive = resource.Body('config_drive')
    #: The current state of the VM.
    state = resource.Body('state')
    #: The driver on which the VM is running.
    driver = resource.Body('driver')
    #: The hypervisor on which the VM is running.
    hypervisor = resource.Body('hypervisor')
    #: The hypervisor OS.
    hypervisor_os = resource.Body('hypervisor_os')
    #: The amount of time in seconds that the VM has been running.
    uptime = resource.Body('uptime')
    #: The number of vCPUs.
    num_cpus = resource.Body('num_cpus')
    #: The number of disks.
    num_disks = resource.Body('num_disks')
    #: The number of vNICs.
    num_nics = resource.Body('num_nics')
    #: The dictionary with information about VM memory usage.
    memory_details = resource.Body('memory_details')
    #: The list of dictionaries with detailed information about VM CPUs.
    cpu_details = resource.Body('cpu_details')
    #: The list of dictionaries with detailed information about VM disks.
    disk_details = resource.Body('disk_details')
    #: The list of dictionaries with detailed information about VM NICs.
    nic_details = resource.Body('nic_details')
    #: The ID for the server.
    server_id = resource.URI('server_id')
