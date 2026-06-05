# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

from typing import Any

from keystoneauth1 import adapter
import requests

from openstack import exceptions
from openstack import resource
from openstack import utils


class ShareReplica(resource.Resource):
    resource_key = "share_replica"
    resources_key = "share_replicas"
    base_path = "share-replicas"

    # capbilities
    allow_create = True
    allow_fetch = True
    allow_commit = False
    allow_delete = True
    allow_list = True
    allow_head = False

    #: properties
    #: The UUID of the share from which to create a share replica.
    share_id = resource.Body("share_id", type=str)
    #: The status of a share replica. List of possible values: available,
    #: error, creating, deleting, or error_deleting.
    status = resource.Body("status", type=str)
    #: If the share replica has its cast_rules_to_readonly attribute set
    #: to True, all existing access rules will be cast to read/only.
    cast_rules_to_readonly = resource.Body("cast_rules_to_readonly", type=bool)
    #: The date and time stamp when the resource was last updated within the
    #: service's database. If a resource was never updated after it was
    #: created, the value of this parameter is set to null.
    updated_at = resource.Body("updated_at", type=str)
    #: The share network ID where the resource is exported to.
    share_network_id = resource.Body("share_network_id", type=str)
    #: The UUID of the share server.
    share_server_id = resource.Body("share_server_id", type=str)
    #: The host name of the share replica.
    host = resource.Body("host", type=str)
    #: The replica state of a share replica.
    replica_state = resource.Body("replica_state", type=str)
    #: The date and time stamp when the resource was created within the
    #: service's database.
    created_at = resource.Body("created_at", type=str)

    def _action(
        self,
        session: adapter.Adapter,
        body: dict[str, Any],
        microversion: str | None = None,
    ) -> requests.Response:
        """Preform server actions given the message body."""
        url = utils.urljoin(self.base_path, self.id, 'action')
        headers = {'Accept': ''}
        microversion = microversion or self._get_microversion(session)
        response = session.post(
            url, json=body, headers=headers, microversion=microversion
        )
        exceptions.raise_from_response(response)
        return response

    def reset_status(
        self, session: adapter.Adapter, status: str
    ) -> requests.Response:
        """Reset the status of the share replica"""
        body = {'reset_status': {'status': status}}
        return self._action(session, body)

    def reset_replica_state(
        self, session: adapter.Adapter, replica_state: str
    ) -> requests.Response:
        """Reset replica_state of the share replica"""
        body = {'reset_replica_state': {'replica_state': replica_state}}
        return self._action(session, body)

    def force_delete(
        self, session: adapter.Adapter, *, ignore_missing: bool = False
    ) -> requests.Response:
        """Force-delete share replica"""
        try:
            body = {'force_delete': None}
        except exceptions.ResourceNotFound:
            if not ignore_missing:
                raise
        return self._action(session, body)

    def promote(self, session: adapter.Adapter) -> requests.Response:
        """Promote share replica"""
        body = {'promote': None}
        return self._action(session, body)

    def resync(self, session: adapter.Adapter) -> requests.Response:
        """Resync share replica"""
        body = {'resync': None}
        return self._action(session, body)
