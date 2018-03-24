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

from openstack.network import network_service
from openstack import resource
from openstack import utils


class Trunk(resource.Resource):
    resource_key = 'trunk'
    resources_key = 'trunks'
    base_path = '/trunks'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'name', 'description', 'port_id', 'status', 'sub_ports',
        project_id='tenant_id',
        is_admin_state_up='admin_state_up',
    )

    # Properties
    #: Trunk name.
    name = resource.Body('name')
    #: The ID of the project who owns the trunk. Only administrative
    #: users can specify a project ID other than their own.
    project_id = resource.Body('tenant_id')
    #: The trunk description.
    description = resource.Body('description')
    #: The administrative state of the port, which is up ``True`` or
    #: down ``False``. *Type: bool*
    is_admin_state_up = resource.Body('admin_state_up', type=bool)
    #: The ID of the trunk's parent port
    port_id = resource.Body('port_id')
    #: The status for the trunk. Possible values are ACTIVE, DOWN, BUILD,
    #: DEGRADED, and ERROR.
    status = resource.Body('status')
    #: A list of ports associated with the trunk.
    sub_ports = resource.Body('sub_ports', type=list)

    def add_subports(self, session, subports):
        url = utils.urljoin('/trunks', self.id, 'add_subports')
        session.put(url, json={'sub_ports': subports})
        self._body.attributes.update({'sub_ports': subports})
        return self

    def delete_subports(self, session, subports):
        url = utils.urljoin('/trunks', self.id, 'remove_subports')
        session.put(url, json={'sub_ports': subports})
        self._body.attributes.update({'sub_ports': subports})
        return self

    def get_subports(self, session):
        url = utils.urljoin('/trunks', self.id, 'get_subports')
        resp = session.get(url)
        self._body.attributes.update(resp.json())
        return resp.json()
