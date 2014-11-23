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

from openstack.identity import identity_service
from openstack import resource


class Extension(resource.Resource):
    resource_key = 'extension'
    resources_key = 'extensions'
    base_path = '/extensions'
    service = identity_service.IdentityService()

    # capabilities
    allow_list = True

    # Properties
    alias = resource.prop('alias')
    description = resource.prop('description')
    links = resource.prop('links')
    name = resource.prop('name')
    namespace = resource.prop('namespace')
    updated = resource.prop('updated')

    @classmethod
    def list(cls, session, **params):
        resp = session.get(cls.base_path, service=cls.service, params=params)
        for data in resp.body[cls.resources_key]['values']:
            yield cls.existing(**data)
