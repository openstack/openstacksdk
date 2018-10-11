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


class Driver(resource.Resource):

    resources_key = 'drivers'
    base_path = '/drivers'

    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = True

    _query_mapping = resource.QueryParameters(details='detail')

    # The BIOS interface fields introduced in 1.40 (Rocky).
    _max_microversion = '1.40'

    #: A list of active hosts that support this driver.
    hosts = resource.Body('hosts', type=list)
    #: A list of relative links, including the self and bookmark links.
    links = resource.Body('links', type=list)
    #: The name of the driver
    name = resource.Body('name', alternate_id=True)
    #: A list of links to driver properties.
    properties = resource.Body('properties', type=list)

    # Hardware interface properties grouped together for convenience,
    # available with detail=True.

    #: Default BIOS interface implementation.
    #: Introduced in API microversion 1.40.
    default_bios_interface = resource.Body("default_bios_interface")
    #: Default boot interface implementation.
    #: Introduced in API microversion 1.30.
    default_boot_interface = resource.Body("default_boot_interface")
    #: Default console interface implementation.
    #: Introduced in API microversion 1.30.
    default_console_interface = resource.Body("default_console_interface")
    #: Default deploy interface implementation.
    #: Introduced in API microversion 1.30.
    default_deploy_interface = resource.Body("default_deploy_interface")
    #: Default inspect interface implementation.
    #: Introduced in API microversion 1.30.
    default_inspect_interface = resource.Body("default_inspect_interface")
    #: Default management interface implementation.
    #: Introduced in API microversion 1.30.
    default_management_interface = resource.Body(
        "default_management_interface")
    #: Default network interface implementation.
    #: Introduced in API microversion 1.30.
    default_network_interface = resource.Body("default_network_interface")
    #: Default port interface implementation.
    #: Introduced in API microversion 1.30.
    default_power_interface = resource.Body("default_power_interface")
    #: Default RAID interface implementation.
    #: Introduced in API microversion 1.30.
    default_raid_interface = resource.Body("default_raid_interface")
    #: Default rescue interface implementation.
    #: Introduced in API microversion 1.38.
    default_rescue_interface = resource.Body("default_rescue_interface")
    #: Default storage interface implementation.
    #: Introduced in API microversion 1.33.
    default_storage_interface = resource.Body("default_storage_interface")
    #: Default vendor interface implementation.
    #: Introduced in API microversion 1.30.
    default_vendor_interface = resource.Body("default_vendor_interface")

    #: Enabled BIOS interface implementations.
    #: Introduced in API microversion 1.40.
    enabled_bios_interfaces = resource.Body("enabled_bios_interfaces")
    #: Enabled boot interface implementations.
    #: Introduced in API microversion 1.30.
    enabled_boot_interfaces = resource.Body("enabled_boot_interfaces")
    #: Enabled console interface implementations.
    #: Introduced in API microversion 1.30.
    enabled_console_interfaces = resource.Body("enabled_console_interfaces")
    #: Enabled deploy interface implementations.
    #: Introduced in API microversion 1.30.
    enabled_deploy_interfaces = resource.Body("enabled_deploy_interfaces")
    #: Enabled inspect interface implementations.
    #: Introduced in API microversion 1.30.
    enabled_inspect_interfaces = resource.Body("enabled_inspect_interfaces")
    #: Enabled management interface implementations.
    #: Introduced in API microversion 1.30.
    enabled_management_interfaces = resource.Body(
        "enabled_management_interfaces")
    #: Enabled network interface implementations.
    #: Introduced in API microversion 1.30.
    enabled_network_interfaces = resource.Body("enabled_network_interfaces")
    #: Enabled port interface implementations.
    #: Introduced in API microversion 1.30.
    enabled_power_interfaces = resource.Body("enabled_power_interfaces")
    #: Enabled RAID interface implementations.
    #: Introduced in API microversion 1.30.
    enabled_raid_interfaces = resource.Body("enabled_raid_interfaces")
    #: Enabled rescue interface implementations.
    #: Introduced in API microversion 1.38.
    enabled_rescue_interfaces = resource.Body("enabled_rescue_interfaces")
    #: Enabled storage interface implementations.
    #: Introduced in API microversion 1.33.
    enabled_storage_interfaces = resource.Body("enabled_storage_interfaces")
    #: Enabled vendor interface implementations.
    #: Introduced in API microversion 1.30.
    enabled_vendor_interfaces = resource.Body("enabled_vendor_interfaces")
