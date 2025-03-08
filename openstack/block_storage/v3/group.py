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


class Group(resource.Resource):
    resource_key = "group"
    resources_key = "groups"
    base_path = "/groups"

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = True
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

    availability_zone = resource.Body("availability_zone")
    created_at = resource.Body("created_at")
    description = resource.Body("description")
    group_snapshot_id = resource.Body("group_snapshot_id")
    group_type = resource.Body("group_type")
    project_id = resource.Body("project_id")
    replication_status = resource.Body("replication_status")
    source_group_id = resource.Body("source_group_id")
    status = resource.Body("status")
    volumes = resource.Body("volumes", type=list)
    volume_types = resource.Body("volume_types", type=list)

    _max_microversion = "3.38"

    def _action(self, session, body):
        """Preform group actions given the message body."""
        session = self._get_session(session)
        microversion = self._get_microversion(session)
        url = utils.urljoin(self.base_path, self.id, 'action')
        response = session.post(url, json=body, microversion=microversion)
        exceptions.raise_from_response(response)
        return response

    def delete(self, session, *args, delete_volumes=False, **kwargs):
        """Delete a group."""
        body = {'delete': {'delete-volumes': delete_volumes}}
        self._action(session, body)

    def reset_status(self, session, status):
        """Resets the status for a group."""
        body = {'reset_status': {'status': status}}
        self._action(session, body)

    def reset(self, session, status):
        warnings.warn(
            "reset is a deprecated alias for reset_status and will be "
            "removed in a future release.",
            os_warnings.RemovedInSDK60Warning,
        )
        self.reset_status(session, status)

    @classmethod
    def create_from_source(
        cls,
        session,
        group_snapshot_id,
        source_group_id,
        name=None,
        description=None,
    ):
        """Creates a new group from source."""
        session = cls._get_session(session)
        microversion = cls._get_microversion(session)
        url = utils.urljoin(cls.base_path, 'action')
        body = {
            'create-from-src': {
                'name': name,
                'description': description,
                'group_snapshot_id': group_snapshot_id,
                'source_group_id': source_group_id,
            }
        }
        response = session.post(url, json=body, microversion=microversion)
        exceptions.raise_from_response(response)

        group = Group()
        group._translate_response(response)
        return group
