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

from openstack.compute import compute_service
from openstack import resource


class ServerMetadata(resource.Resource):
    resource_key = 'metadata'
    id_attribute = 'server_id'
    base_path = '/servers/%(server_id)s/metadata'
    service = compute_service.ComputeService()

    # capabilities
    allow_create = True
    allow_retrieve = True
    allow_update = True

    # Properties
    server_id = resource.prop('server_id')

    @classmethod
    def create_by_id(cls, session, attrs, resource_id=None, path_args=None):
        no_id = attrs.copy()
        no_id.pop('server_id')
        body = {"metadata": no_id}
        url = cls.base_path % path_args
        resp = session.put(url, service=cls.service, json=body).body
        attrs = resp["metadata"].copy()
        attrs['server_id'] = resource_id
        return attrs

    @classmethod
    def get_data_by_id(cls, session, resource_id, path_args=None,
                       include_headers=False):
        url = cls.base_path % path_args
        resp = session.get(url, service=cls.service).body
        return resp[cls.resource_key]

    @classmethod
    def update_by_id(cls, session, resource_id, attrs, path_args=None):
        return cls.create_by_id(session, attrs, resource_id, path_args)
