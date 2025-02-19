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

import typing as ty

from keystoneauth1 import adapter
import requests

from openstack.baremetal.v1 import _common
from openstack import exceptions
from openstack import resource
from openstack import utils


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
    # The firmware interface fields introduced in 1.86.
    _max_microversion = '1.86'

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
    #: Default firmware interface implementation.
    #: Introduced in API microversion 1.86.
    default_firmware_interface = resource.Body("default_firmware_interface")
    #: Default inspect interface implementation.
    #: Introduced in API microversion 1.30.
    default_inspect_interface = resource.Body("default_inspect_interface")
    #: Default management interface implementation.
    #: Introduced in API microversion 1.30.
    default_management_interface = resource.Body(
        "default_management_interface"
    )
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
    #: Enabled firmware interface implementations.
    #: Introduced in API microversion 1.86.
    enabled_firmware_interfaces = resource.Body("enabled_firmware_interfaces")
    #: Enabled inspect interface implementations.
    #: Introduced in API microversion 1.30.
    enabled_inspect_interfaces = resource.Body("enabled_inspect_interfaces")
    #: Enabled management interface implementations.
    #: Introduced in API microversion 1.30.
    enabled_management_interfaces = resource.Body(
        "enabled_management_interfaces"
    )
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

    def list_vendor_passthru(self, session):
        """Fetch vendor specific methods exposed by driver

        :param session: The session to use for making this request.
        :returns: A dict of the available vendor passthru methods for driver.
            Method names keys and corresponding usages in dict form as values
            Usage dict properties:
            * ``async``: bool # Is passthru function invoked asynchronously
            * ``attach``: bool # Is return value attached to response object
            * ``description``: str # Description of what the method does
            * ``http_methods``: list # List of HTTP methods supported
        """
        session = self._get_session(session)
        request = self._prepare_request()
        request.url = utils.urljoin(request.url, 'vendor_passthru', 'methods')
        response = session.get(request.url, headers=request.headers)

        msg = "Failed to list list vendor_passthru methods for {driver_name}"
        exceptions.raise_from_response(
            response, error_message=msg.format(driver_name=self.name)
        )
        return response.json()

    def call_vendor_passthru(
        self,
        session: adapter.Adapter,
        verb: str,
        method: str,
        body: ty.Optional[dict] = None,
    ) -> requests.Response:
        """Call a vendor specific passthru method

        Contents of body are params passed to the hardware driver
        function. Validation happens there. Missing parameters, or
        excess parameters will cause the request to be rejected

        :param session: The session to use for making this request.
        :param method: Vendor passthru method name.
        :param verb: One of GET, POST, PUT, DELETE,
            depending on the driver and method.
        :param body: passed to the vendor function as json body.
        :raises: :exc:`ValueError` if :data:`verb` is not one of
            GET, POST, PUT, DELETE
        :returns: response of method call.
        """
        if verb.upper() not in ['GET', 'PUT', 'POST', 'DELETE']:
            raise ValueError(f'Invalid verb: {verb}')

        session = self._get_session(session)
        request = self._prepare_request()
        request.url = utils.urljoin(
            request.url, f'vendor_passthru?method={method}'
        )
        call = getattr(session, verb.lower())
        response = call(
            request.url,
            json=body,
            headers=request.headers,
            retriable_status_codes=_common.RETRIABLE_STATUS_CODES,
        )

        msg = f"Failed call to method {method} on driver {self.name}"
        exceptions.raise_from_response(response, error_message=msg)
        return response
