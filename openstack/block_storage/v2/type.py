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


class Type(resource.Resource):
    resource_key = "volume_type"
    resources_key = "volume_types"
    base_path = "/types"

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_list = True

    _query_mapping = resource.QueryParameters("is_public")

    # Properties
    #: A dict of extra specifications. "capabilities" is a usual key.
    extra_specs = resource.Body("extra_specs", type=dict)
    #: a private volume-type. *Type: bool*
    is_public = resource.Body('os-volume-type-access:is_public', type=bool)

    def get_private_access(self, session):
        """List projects with private access to the volume type.

        :param session: The session to use for making this request.
        :returns: The volume type access response.
        """
        url = utils.urljoin(self.base_path, self.id, "os-volume-type-access")
        resp = session.get(url)

        exceptions.raise_from_response(resp)

        return resp.json().get("volume_type_access", [])

    def add_private_access(self, session, project_id):
        """Add project access from the volume type.

        :param session: The session to use for making this request.
        :param project_id: The project to add access for.
        """
        url = utils.urljoin(self.base_path, self.id, "action")
        body = {"addProjectAccess": {"project": project_id}}

        resp = session.post(url, json=body)

        exceptions.raise_from_response(resp)

    def remove_private_access(self, session, project_id):
        """Remove project access from the volume type.

        :param session: The session to use for making this request.
        :param project_id: The project to remove access for.
        """
        url = utils.urljoin(self.base_path, self.id, "action")
        body = {"removeProjectAccess": {"project": project_id}}

        resp = session.post(url, json=body)

        exceptions.raise_from_response(resp)
