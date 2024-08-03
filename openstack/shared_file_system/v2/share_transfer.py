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

from openstack import resource, exceptions, utils


class ShareTransfer(resource.Resource):
    resource_key = "transfer"
    base_path = "/share-transfers"

    # capabilities
    allow_list = True
    allow_create = True
    allow_fetch = True
    allow_commit = False
    allow_delete = True
    allow_head = False

    _query_mapping = resource.QueryParameters(
        "id",
        "share_id",
        "name",
        "auth_key",
        "clear_access_rules",
        "all_tenants",
        "destination_project_id",
        "limit",
        "offset",
        "sort_key",
        "sort_dir",
    )
    # Properties
    #: The transfer UUID.
    id = resource.Body("id", type=str)
    #: The share UUID.
    share_id = resource.Body("share_id", type=str)
    #: The date and time stamp when the resource was created
    #: within the service's database.
    created_at = resource.Body("created_at", type=str)
    #: The transfer display name.
    name = resource.Body("name", type=str)
    #: The type of the resource for the transfer.
    resource_type = resource.Body("resource_type", type=str)
    #: The UUID of the resource for the transfer.
    resource_id = resource.Body("resource_id", type=str)
    #: The authentication key for the transfer.
    auth_key = resource.Body("auth_key", type=str)
    #: The ID of the project that owns the resource.
    source_project_id = resource.Body("source_project_id", type=str)
    #: UUID of the destination project to accept transfer resource.
    destination_project_id = resource.Body("destination_project_id", type=str)
    #: Whether the transfer has been accepted.
    accepted = resource.Body("accepted", type=bool)
    #: The date and time stamp when the resource transfer will expire
    #: After transfer expired, will be automatically deleted
    expires_at = resource.Body("expires_at", type=str)
    #: Pagination and bookmark links for the resource.
    links = resource.Body("links", type=list)

    def accept(
        self,
        session: adapter.Adapter,
        *,
        auth_key: str,
        clear_access_rules: bool = False,
    ) -> Self:
        """Accept a share transfer using the auth_key."""

        url = utils.urljoin(self.base_path, self.id, "accept")
        body = {
            "accept": {
                "auth_key": auth_key,
                "clear_access_rules": clear_access_rules,
            }
        }

        response = session.post(url, json=body)

        exceptions.raise_from_response(response)
        self._translate_response(response)
        return self
