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


class User(resource.Resource):
    resource_key = 'user'
    resources_key = 'users'
    base_path = '/instances/%(instance_id)s/users'
    service = database_service.DatabaseService()

    # capabilities
    allow_create = True
    allow_delete = True
    allow_list = True

    instance_id = resource.URI('instance_id')

    # Properties
    #: Databases the user has access to
    databases = resource.Body('databases')
    #: The name of the user
    name = resource.Body('name', alternate_id=True)
    #: The password of the user
    password = resource.Body('password')

    def _prepare_request(self, requires_id=True, prepend_key=True):
        """Prepare a request for the database service's create call

        User.create calls require the resources_key.
        The base_prepare_request would insert the resource_key (singular)
        """
        body = {self.resources_key: self._body.dirty}

        uri = self.base_path % self._uri.attributes
        uri = utils.urljoin(uri, self.id)

        return resource._Request(uri, body, None)
