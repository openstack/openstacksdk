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

import warnings

from openstack import exceptions
from openstack import resource
from openstack import utils
from openstack import warnings as os_warnings


class GroupSnapshot(resource.Resource):
    resource_key = "group_snapshot"
    resources_key = "group_snapshots"
    base_path = "/group_snapshots"

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = False
    allow_list = True

    _query_mapping = resource.QueryParameters(
        "limit",
        "marker",
        "offset",
        "sort_dir",
        "sort_key",
        "sort",
        all_projects="all_tenants",
    )

    #: Properties
    #: The date and time when the resource was created.
    created_at = resource.Body("created_at")
    #: The group snapshot description.
    description = resource.Body("description")
    #: The UUID of the source group.
    group_id = resource.Body("group_id")
    #: The group type ID.
    group_type_id = resource.Body("group_type_id")
    #: The ID of the group snapshot.
    id = resource.Body("id")
    #: The group snapshot name.
    name = resource.Body("name")
    #: The UUID of the volume group snapshot project.
    project_id = resource.Body("project_id")
    #: The status of the generic group snapshot.
    status = resource.Body("status")

    # Pagination support was added in microversion 3.29
    _max_microversion = '3.29'

    def _action(self, session, body, microversion=None):
        """Preform aggregate actions given the message body."""
        url = utils.urljoin(self.base_path, self.id, 'action')
        headers = {'Accept': ''}
        # TODO(stephenfin): This logic belongs in openstack.resource I suspect
        if microversion is None:
            if session.default_microversion:
                microversion = session.default_microversion
            else:
                microversion = utils.maximum_supported_microversion(
                    session,
                    self._max_microversion,
                )
        response = session.post(
            url,
            json=body,
            headers=headers,
            microversion=microversion,
        )
        exceptions.raise_from_response(response)
        return response

    def reset_status(self, session, state):
        """Resets the status for a group snapshot."""
        body = {'reset_status': {'status': state}}
        return self._action(session, body)

    def reset_state(self, session, status):
        warnings.warn(
            "reset_state is a deprecated alias for reset_status and will be "
            "removed in a future release.",
            os_warnings.RemovedInSDK60Warning,
        )
        self.reset_status(session, status)
