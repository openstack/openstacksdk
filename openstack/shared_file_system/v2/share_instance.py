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

from openstack import exceptions
from openstack import resource
from openstack import utils


class ShareInstance(resource.Resource):
    resource_key = "share_instance"
    resources_key = "share_instances"
    base_path = "/share_instances"

    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = True
    allow_head = False

    #: Properties
    #: The share instance access rules status. A valid value is active,
    #: error, or syncing.
    access_rules_status = resource.Body("access_rules_status", type=str)
    #: The name of the availability zone the share exists within.
    availability_zone = resource.Body("availability_zone", type=str)
    #: If the share instance has its cast_rules_to_readonly attribute
    #: set to True, all existing access rules be cast to read/only.
    cast_rules_to_readonly = resource.Body("cast_rules_to_readonly", type=bool)
    #: The date and time stamp when the resource was created within the
    #: service’s database.
    created_at = resource.Body("created_at", type=str)
    #: The host name of the service back end that the resource is
    #: contained within.
    host = resource.Body("host", type=str)
    #: The progress of the share creation.
    progress = resource.Body("progress", type=str)
    #: The share replica state. Has set value only when replication is used.
    #: List of possible values: active, in_sync, out_of_sync, error
    replica_state = resource.Body("replica_state", type=str)
    #: The UUID of the share to which the share instance belongs to.
    share_id = resource.Body("share_id", type=str)
    #: The share network ID where the resource is exported to.
    share_network_id = resource.Body("share_network_id", type=str)
    #: The UUID of the share server.
    share_server_id = resource.Body("share_server_id", type=str)
    #: The share or share instance status.
    status = resource.Body("status", type=str)

    def _action(self, session, body, microversion=None):
        """Perform share instance actions given the message body"""
        url = utils.urljoin(self.base_path, self.id, 'action')
        headers = {'Accept': ''}
        extra_attrs = {}
        if microversion:
            # Set microversion override
            extra_attrs['microversion'] = microversion
        else:
            extra_attrs['microversion'] = self._get_microversion(session)
        response = session.post(url, json=body, headers=headers, **extra_attrs)
        exceptions.raise_from_response(response)
        return response

    def reset_status(self, session, reset_status):
        """Reset share instance to given status"""
        body = {"reset_status": {"status": reset_status}}
        self._action(session, body)

    def force_delete(self, session):
        """Force delete share instance"""
        body = {"force_delete": None}
        self._action(session, body)
