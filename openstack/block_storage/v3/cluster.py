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


class Cluster(resource.Resource):
    resource_key = 'cluster'
    resources_key = 'clusters'
    base_path = '/clusters'

    # capabilities
    allow_fetch = True
    allow_list = True

    _max_microversion = '3.26'

    _query_mapping = resource.QueryParameters(
        'name',
        'binary',
        'is_up',
        'disabled',
        'num_hosts',
        'num_down_hosts',
        'replication_status',
        'frozen',
        'active_backend_id',
    )

    # Properties
    #: The ID of active storage backend (cinder-volume services only).
    active_backend_id = resource.Body('active_backend_id')
    #: The binary name of the services in the cluster.
    binary = resource.Body('binary')
    #: The date and time when the resource was created.
    created_at = resource.Body('created_at')
    #: The reason for disabling the cluster.
    disabled_reason = resource.Body('disabled_reason')
    #: Whether the cluster is frozen for replication.
    frozen = resource.Body('frozen', type=bool)
    #: The last periodic heartbeat received.
    last_heartbeat = resource.Body('last_heartbeat')
    #: The name of the cluster.
    name = resource.Body('name', alternate_id=True)
    #: The number of down hosts in the cluster.
    num_down_hosts = resource.Body('num_down_hosts', type=int)
    #: The number of hosts in the cluster.
    num_hosts = resource.Body('num_hosts', type=int)
    #: The cluster replication status.
    replication_status = resource.Body('replication_status')
    #: The state of the cluster. One of ``up`` or ``down``.
    state = resource.Body('state')
    #: The status of the cluster. One of ``enabled`` or ``disabled``.
    status = resource.Body('status')
    #: The date and time when the resource was last updated.
    updated_at = resource.Body('updated_at')

    def _action(
        self,
        session: adapter.Adapter,
        action: str,
        body: dict[str, Any],
    ) -> Self:
        url = utils.urljoin(Cluster.base_path, action)
        microversion = session.default_microversion
        response = session.put(url, json=body, microversion=microversion)
        self._translate_response(response)
        return self

    def enable(self, session: adapter.Adapter) -> Self:
        """Enable scheduling for the cluster."""
        body: dict[str, Any] = {'name': self.name}
        if self.binary:
            body['binary'] = self.binary
        return self._action(session, 'enable', body)

    def disable(
        self,
        session: adapter.Adapter,
        *,
        reason: str | None = None,
    ) -> Self:
        """Disable scheduling for the cluster.

        :param reason: The reason for disabling the cluster.
        """
        body: dict[str, Any] = {'name': self.name}
        if self.binary:
            body['binary'] = self.binary
        if reason:
            body['disabled_reason'] = reason
        return self._action(session, 'disable', body)
