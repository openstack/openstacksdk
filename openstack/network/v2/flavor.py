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
from openstack import resource2 as resource
from openstack import utils


class Flavor(resource.Resource):
    resource_key = 'flavor'
    resources_key = 'flavors'
    base_path = '/flavors'
    service = network_service.NetworkService()

    # capabilities
    allow_create = True
    allow_get = True
    allow_update = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters(
        'description', 'name', 'service_type', is_enabled='enabled')

    # properties
    #: description for the flavor
    description = resource.Body('description')
    #: Sets enabled flag
    is_enabled = resource.Body('enabled', type=bool)
    #: The name of the flavor
    name = resource.Body('name')
    #: Service type to which the flavor applies
    service_type = resource.Body('service_type')
    #: IDs of service profiles associated with this flavor
    service_profile_ids = resource.Body('service_profiles', type=list)

    def associate_flavor_with_service_profile(
            self, session, service_profile_id=None):
        flavor_id = self.id
        url = utils.urljoin(self.base_path, flavor_id, 'service_profiles')
        body = {"service_profile": {"id": service_profile_id}}
        resp = session.post(url, endpoint_filter=self.service, json=body)
        return resp.json()

    def disassociate_flavor_from_service_profile(
            self, session, service_profile_id=None):
        flavor_id = self.id
        url = utils.urljoin(
            self.base_path, flavor_id, 'service_profiles', service_profile_id)
        session.delete(url, endpoint_filter=self.service)
        return None
