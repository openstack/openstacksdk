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

from typing import Self

from keystoneauth1 import adapter

from openstack import exceptions
from openstack import resource
from openstack import utils


class ShareType(resource.Resource):
    resource_key = "share_type"
    resources_key = "share_types"
    base_path = "/types"

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_head = False

    _query_mapping = resource.QueryParameters("is_public", "extra_specs")

    #: Properties
    #: Description of the share type
    description = resource.Body("description", type=str)
    #: List of extra specs for share types
    extra_specs = resource.Body("extra_specs", type=dict, default={})
    #: Indicates if share type is default
    is_default = resource.Body("is_default", type=bool)
    #: Indicates if share type is public
    is_public = resource.Body("share_type_access:is_public", type=bool)
    #: List of required extra specs for share types
    required_extra_specs = resource.Body("required_extra_specs", type=dict)

    def set_extra_specs(self, session: adapter.Adapter, **specs: str) -> Self:
        """Update extra_specs

        This call will replace only the extra_specs with the same keys
        given here.  Other keys will not be modified.

        :param session: The session to use for this request.
        :param extra_specs: key/value extra_specs pairs to set or update
        :returns: Updated self
        """
        url = utils.urljoin(self.base_path, self.id, 'extra_specs')
        microversion = self._get_microversion(session)
        response = session.post(
            url, json={'extra_specs': specs}, microversion=microversion
        )
        exceptions.raise_from_response(response)
        specs = response.json()['extra_specs']
        self._update(extra_specs=specs)
        return self

    def delete_extra_specs_property(
        self, session: adapter.Adapter, prop: str
    ) -> None:
        """Delete extra specs

        :param session: The session to use for this request.
        :param prop: The property to delete.
        :returns: None
        """
        url = utils.urljoin(self.base_path, self.id, "extra_specs", prop)
        microversion = self._get_microversion(session)
        response = session.delete(url, microversion=microversion)
        exceptions.raise_from_response(response)
