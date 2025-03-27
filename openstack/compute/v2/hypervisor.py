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

import warnings

from openstack import exceptions
from openstack import resource
from openstack import utils
from openstack import warnings as os_warnings


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

    # Lot of attributes are dropped in 2.88
    _max_microversion = '2.88'

    # Properties
    #: Information about the hypervisor's CPU. Up to 2.28 it was string.
    cpu_info = resource.Body('cpu_info')
    #: IP address of the host
    host_ip = resource.Body('host_ip')
    #: The type of hypervisor
    hypervisor_type = resource.Body('hypervisor_type')
    #: Version of the hypervisor
    hypervisor_version = resource.Body('hypervisor_version')
    #: Name of hypervisor
    name = resource.Body('hypervisor_hostname')
    #: Service details
    service_details = resource.Body('service', type=dict)
    #: List of Servers
    servers = resource.Body('servers', type=list, list_type=dict)
    #: State of hypervisor
    state = resource.Body('state')
    #: Status of hypervisor
    status = resource.Body('status')
    #: The total uptime of the hypervisor and information about average load.
    #: This attribute is set only when querying uptime explicitly.
    uptime = resource.Body('uptime')

    # Attributes deprecated with 2.88
    #: Measurement of the hypervisor's current workload
    current_workload = resource.Body('current_workload', deprecated=True)
    #: Disk space available to the scheduler
    disk_available = resource.Body("disk_available_least", deprecated=True)
    #: The amount, in gigabytes, of local storage used
    local_disk_used = resource.Body('local_gb_used', deprecated=True)
    #: The amount, in gigabytes, of the local storage device
    local_disk_size = resource.Body('local_gb', deprecated=True)
    #: The amount, in gigabytes, of free space on the local storage device
    local_disk_free = resource.Body('free_disk_gb', deprecated=True)
    #: The amount, in megabytes, of memory
    memory_used = resource.Body('memory_mb_used', deprecated=True)
    #: The amount, in megabytes, of total memory
    memory_size = resource.Body('memory_mb', deprecated=True)
    #: The amount, in megabytes, of available memory
    memory_free = resource.Body('free_ram_mb', deprecated=True)
    #: Count of the running virtual machines
    running_vms = resource.Body('running_vms', deprecated=True)
    #: Count of the VCPUs in use
    vcpus_used = resource.Body('vcpus_used', deprecated=True)
    #: Count of all VCPUs
    vcpus = resource.Body('vcpus', deprecated=True)

    def get_uptime(self, session):
        """Get uptime information for the hypervisor

        Updates uptime attribute of the hypervisor object
        """
        warnings.warn(
            "This call is deprecated and is only available until Nova 2.88",
            os_warnings.LegacyAPIWarning,
        )
        if utils.supports_microversion(session, '2.88'):
            raise exceptions.SDKException(
                'Hypervisor.get_uptime is not supported anymore'
            )
        url = utils.urljoin(self.base_path, self.id, 'uptime')
        microversion = self._get_microversion(session)
        response = session.get(url, microversion=microversion)
        self._translate_response(response)
        return self


HypervisorDetail = Hypervisor
