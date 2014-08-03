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

from openstack.database import database_service
from openstack import resource
from openstack import utils


class Instance(resource.Resource):
    resource_key = 'instance'
    resources_key = 'instances'
    base_path = '/instances'
    service = database_service.DatabaseService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True
    allow_delete = True
    allow_list = True

    # Properties
    flavor = resource.prop('flavor')
    links = resource.prop('links')
    name = resource.prop('name')
    status = resource.prop('status')
    volume = resource.prop('volume')

    def enable_root_user(self, session):
        url = utils.urljoin(self.base_path, self.id, 'root')
        resp = session.post(url, service=self.service).body
        return resp['user']

    def is_root_enabled(self, session):
        url = utils.urljoin(self.base_path, self.id, 'root')
        resp = session.get(url, service=self.service).body
        return resp['rootEnabled']

    def restart(self, session):
        body = {'restart': {}}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, service=self.service, json=body)

    def resize(self, session, flavor_reference):
        body = {'resize': {'flavorRef': flavor_reference}}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, service=self.service, json=body)

    def resize_volume(self, session, volume_size):
        body = {'resize': {'volume': volume_size}}
        url = utils.urljoin(self.base_path, self.id, 'action')
        session.post(url, service=self.service, json=body)
