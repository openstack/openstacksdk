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

from typing import Any, Self

from keystoneauth1 import adapter

from openstack import exceptions
from openstack import resource
from openstack import utils


class ConsistencyGroup(resource.Resource):
    resource_key = "consistencygroup"
    resources_key = "consistencygroups"
    base_path = "/consistencygroups"

    _query_mapping = resource.QueryParameters(
        "limit",
        "marker",
        "offset",
        "sort_dir",
        "sort_key",
        "sort",
    )

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = True
    allow_list = True

    # Properties
    #: The availability zone.
    availability_zone = resource.Body("availability_zone")
    #: The date and time when this resource was created.
    created_at = resource.Body("created_at")
    #: The description.
    description = resource.Body("description")
    #: The name.
    name = resource.Body("name")
    #: The status.
    status = resource.Body("status")
    #: The volume types.
    volume_types = resource.Body("volume_types", type=list)
    #: Comma-separated list of volume UUIDs to add to the consistency group.
    #: Used in update requests only.
    add_volumes = resource.Body("add_volumes")
    #: Comma-separated list of volume UUIDs to remove from the consistency
    #: group. Used in update requests only.
    remove_volumes = resource.Body("remove_volumes")

    @classmethod
    def create_from_source(
        cls,
        session: adapter.Adapter,
        *,
        consistency_group_snapshot_id: str | None = None,
        consistency_group_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> Self:
        """Creates a new group from source.

        :param session: The session to use for making this request
        :param consistency_group_snapshot_id: The ID of a consistency group
            snapshot to create the new consistency group from. Either this or
            consistency_group_id must be provided
        :param consistency_group_id: The ID of a consistency group to create
            the new consistency group from. Either this or
            consistency_group_snapshot_id must be provided
        :param name: The name to assign to the new consistency group
        :param description: The description to set on the new consistency
            group
        :returns: The created consistency group
        """
        session = cls._get_session(session)
        microversion = cls._get_microversion(session)
        url = utils.urljoin(cls.base_path, 'create_from_src')
        body = {
            'consistencygroup-from-src': {
                'name': name,
                'description': description,
                'cgsnapshot_id': consistency_group_snapshot_id,
                'source_cgid': consistency_group_id,
            }
        }
        response = session.post(url, json=body, microversion=microversion)
        exceptions.raise_from_response(response)

        cg = cls()
        cg._translate_response(response=response)
        return cg

    def delete(
        self,
        session: adapter.Adapter,
        error_message: str | None = None,
        *,
        microversion: str | None = None,
        base_path: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> Self:
        # consistency group delete is done via a POST, not a DELETE :(
        url = utils.urljoin(self.base_path, self.id, 'delete')
        body: dict[str, Any] = {'consistency_group': {}}
        if params and 'force' in params:
            body['consistency_group']['force'] = params['force']
        response = session.post(url, json=body, microversion=microversion)

        self._translate_response(
            response, has_body=False, error_message=error_message
        )
        return self
