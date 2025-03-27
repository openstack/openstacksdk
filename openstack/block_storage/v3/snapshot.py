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

from openstack.common import metadata
from openstack import exceptions
from openstack import format
from openstack import resource
from openstack import utils
from openstack import warnings as os_warnings


class Snapshot(resource.Resource, metadata.MetadataMixin):
    resource_key = "snapshot"
    resources_key = "snapshots"
    base_path = "/snapshots"

    _query_mapping = resource.QueryParameters(
        "name",
        "status",
        "volume_id",
        "project_id",
        "limit",
        "marker",
        "offset",
        "sort_dir",
        "sort_key",
        "sort",
        all_projects="all_tenants",
    )

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = True
    allow_list = True

    # Properties
    #: Whether this resource consumes quota or not. Resources that not
    #: counted for quota usage are usually temporary internal resources
    #: created to perform an operation.
    #: This is included from microversion 3.65
    consumes_quota = resource.Body("consumes_quota")
    #: The timestamp of this snapshot creation.
    created_at = resource.Body("created_at")
    #: Description of snapshot. Default is None.
    description = resource.Body("description")
    #: The ID of the group snapshot.
    #: This is included from microversion 3.14
    group_snapshot_id = resource.Body("group_snapshot_id")
    #: Indicate whether to create snapshot, even if the volume is attached.
    #: Default is ``False``. *Type: bool*
    is_forced = resource.Body("force", type=format.BoolStr)
    #: The percentage of completeness the snapshot is currently at.
    progress = resource.Body("os-extended-snapshot-attributes:progress")
    #: The project ID this snapshot is associated with.
    project_id = resource.Body("os-extended-snapshot-attributes:project_id")
    #: The size of the volume, in GBs.
    size = resource.Body("size", type=int)
    #: The current status of this snapshot. Potential values are creating,
    #: available, deleting, error, and error_deleting.
    status = resource.Body("status")
    #: The date and time when the resource was updated.
    updated_at = resource.Body("updated_at")
    #: The UUID of the user.
    #: This is included from microversion 3.41
    user_id = resource.Body("user_id")
    #: The ID of the volume this snapshot was taken of.
    volume_id = resource.Body("volume_id")

    _max_microversion = '3.65'

    def _action(self, session, body, microversion=None):
        """Preform backup actions given the message body."""
        url = utils.urljoin(self.base_path, self.id, 'action')
        resp = session.post(
            url, json=body, microversion=self._max_microversion
        )
        exceptions.raise_from_response(resp)
        return resp

    def force_delete(self, session):
        """Force snapshot deletion."""
        body = {'os-force_delete': None}
        self._action(session, body)

    def reset_status(self, session, status):
        """Reset the status of the snapshot."""
        body = {'os-reset_status': {'status': status}}
        self._action(session, body)

    def reset(self, session, status):
        warnings.warn(
            "reset is a deprecated alias for reset_status and will be "
            "removed in a future release.",
            os_warnings.RemovedInSDK60Warning,
        )
        self.reset_status(session, status)

    def set_status(self, session, status, progress=None):
        """Update fields related to the status of a snapshot."""
        body = {'os-update_snapshot_status': {'status': status}}
        if progress is not None:
            body['os-update_snapshot_status']['progress'] = progress
        self._action(session, body)

    @classmethod
    def manage(
        cls,
        session,
        volume_id,
        ref,
        name=None,
        description=None,
        metadata=None,
    ):
        """Manage a snapshot under block storage provisioning."""
        url = '/manageable_snapshots'
        if not utils.supports_microversion(session, '3.8'):
            url = '/os-snapshot-manage'
        body = {
            'snapshot': {
                'volume_id': volume_id,
                'ref': ref,
                'name': name,
                'description': description,
                'metadata': metadata,
            }
        }
        resp = session.post(url, json=body, microversion=cls._max_microversion)
        exceptions.raise_from_response(resp)
        snapshot = Snapshot()
        snapshot._translate_response(resp)
        return snapshot

    def unmanage(self, session):
        """Unmanage a snapshot from block storage provisioning."""
        body = {'os-unmanage': None}
        self._action(session, body)


SnapshotDetail = Snapshot
