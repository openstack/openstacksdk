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

from typing import Any, Self

from keystoneauth1 import adapter

from openstack import resource
from openstack import utils


class Service(resource.Resource):
    resource_key = 'service'
    resources_key = 'services'
    base_path = '/services'

    # capabilities
    allow_create = False
    allow_fetch = False
    allow_commit = True
    allow_delete = False
    allow_list = True
    allow_head = False

    _query_mapping = resource.QueryParameters(
        'name',
        'binary',
        'host',
        'state',
        'status',
        name='binary',
        availability_zone='zone',
    )

    #: Properties
    #: The availability zone of service
    availability_zone = resource.Body('zone')
    #: The service binary name.
    binary = resource.Body('binary', type=str, aka='name')
    #: The service host name.
    host = resource.Body('host', type=str)
    #: Service name
    name = resource.Body('binary')
    #: The current state of the service.
    state = resource.Body('state', type=str)
    #: The service status, which is enabled or disabled.
    status = resource.Body('status', type=str)
    #: The date and time stamp when the resource was
    #: last updated within the service's database.
    updated_at = resource.Body('updated_at', type=str)
    #: The reason for disabling the service.
    disabled_reason = resource.Body('disabled_reason', type=str)
    #: Whether the service is currently ensuring shares.
    ensuring = resource.Body('ensuring', type=dict)

    def _action(
        self,
        session: adapter.Adapter,
        action: str,
        body: dict[str, Any],
        microversion: str | None = None,
    ) -> Self:
        if not microversion:
            microversion = session.default_microversion
        url = utils.urljoin(Service.base_path, action)
        response = session.put(url, json=body, microversion=microversion)
        self._translate_response(response)
        return self

    def enable(self, session: adapter.Adapter) -> Self:
        """Enable service."""
        body = {
            'host': self.host,
            'binary': self.binary,
        }

        return self._action(session, 'enable', body)

    def disable(
        self,
        session: adapter.Adapter,
        disable_reason: str | None = None,
    ) -> Self:
        """Disable service."""
        body: dict[str, Any] = {
            'host': self.host,
            'binary': self.binary,
        }
        if disable_reason:
            body['disabled_reason'] = disable_reason

        return self._action(session, 'disable', body)

    def ensure_shares(self, session: adapter.Adapter) -> None:
        """Ensure shares on a back end."""
        url = utils.urljoin(Service.base_path, 'ensure-shares')
        microversion = session.default_microversion
        session.post(url, json={'host': self.host}, microversion=microversion)
