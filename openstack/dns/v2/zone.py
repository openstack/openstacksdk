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

from openstack.dns.v2 import _base


class Zone(_base.Resource):
    """DNS ZONE Resource"""
    resources_key = 'zones'
    base_path = '/zones'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True

    commit_method = "PATCH"

    _query_mapping = resource.QueryParameters(
        'name', 'type', 'email', 'status', 'description', 'ttl',
        'limit', 'marker'
    )

    #: Properties
    #: current action in progress on the resource
    action = resource.Body('action')
    #: Attributes
    #: Key:Value pairs of information about this zone, and the pool the user
    #: would like to place the zone in. This information can be used by the
    #: scheduler to place zones on the correct pool.
    attributes = resource.Body('attributes', type=dict)
    #: Timestamp when the zone was created
    created_at = resource.Body('created_at')
    #: Zone description
    #: *Type: str*
    description = resource.Body('description')
    #: The administrator email of this zone
    #: *Type: str*
    email = resource.Body('email')
    #: Links contains a `self` pertaining to this zone or a `next` pertaining
    #: to next page
    links = resource.Body('links', type=dict)
    #: The master list for slaver server to fetch DNS
    masters = resource.Body('masters', type=list)
    #: Zone name
    name = resource.Body('name')
    #: The pool which manages the zone, assigned by system
    pool_id = resource.Body('pool_id')
    #: The project id which the zone belongs to
    project_id = resource.Body('project_id')
    #: Serial number in the SOA record set in the zone,
    #: which identifies the change on the primary DNS server
    #: *Type: int*
    serial = resource.Body('serial', type=int)
    #: Zone status
    #: Valid values include `PENDING_CREATE`, `ACTIVE`,
    #: `PENDING_DELETE`, `ERROR`
    status = resource.Body('status')
    #: SOA TTL time, unit is seconds, default 300, TTL range 300-2147483647
    #: *Type: int*
    ttl = resource.Body('ttl', type=int)
    #: Zone type,
    #: Valid values include `PRIMARY`, `SECONDARY`
    #: *Type: str*
    type = resource.Body('type')
    #: Timestamp when the zone was last updated
    updated_at = resource.Body('updated_at')

    def _action(self, session, action, body):
        """Preform actions given the message body.

        """
        url = utils.urljoin(self.base_path, self.id, 'tasks', action)
        response = session.post(
            url,
            json=body)
        exceptions.raise_from_response(response)
        return response

    def abandon(self, session):
        self._action(session, 'abandon', None)

    def xfr(self, session):
        self._action(session, 'xfr', None)
