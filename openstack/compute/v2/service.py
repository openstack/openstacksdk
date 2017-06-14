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
from openstack import utils


class Service(resource2.Resource):
    resource_key = 'service'
    resources_key = 'services'
    base_path = '/os-services'

    service = compute_service.ComputeService()

    # capabilities
    allow_list = True
    allow_update = True

    # Properties
    #: Status of service
    status = resource2.Body('status')
    #: State of service
    state = resource2.Body('state')
    #: Name of service
    binary = resource2.Body('binary')
    #: Id of service
    id = resource2.Body('id')
    #: Disabled reason of service
    disables_reason = resource2.Body('disabled_reason')
    #: Host where service runs
    host = resource2.Body('host')
    #: The availability zone of service
    zone = resource2.Body("zone")

    def _action(self, session, action, body):
        url = utils.urljoin(Service.base_path, action)
        return session.put(url, endpoint_filter=self.service, json=body)

    def force_down(self, session, host, binary):
        """Force a service down."""

        body = {
            'host': host,
            'binary': binary,
            'forced_down': True,
        }

        return self._action(session, 'force-down', body)

    def enable(self, session, host, binary):
        """Enable service."""
        body = {
            'host': host,
            'binary': binary,
        }

        return self._action(session, 'enable', body)

    def disable(self, session, host, binary, reason=None):
        """Disable service."""
        body = {
            'host': host,
            'binary': binary,
        }

        if not reason:
            action = 'disable'
        else:
            body['disabled_reason'] = reason
            action = 'disable-log-reason'

        return self._action(session, action, body)
