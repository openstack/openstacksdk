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

from openstack.common import metadata
from openstack import exceptions
from openstack import format
from openstack import resource
from openstack import utils


class Snapshot(resource.Resource, metadata.MetadataMixin):
    resource_key = "snapshot"
    resources_key = "snapshots"
    base_path = "/snapshots"

    _query_mapping = resource.QueryParameters(
        'name', 'status', 'volume_id',
        'project_id', all_projects='all_tenants')

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = True
    allow_list = True

    # Properties
    #: The timestamp of this snapshot creation.
    created_at = resource.Body("created_at")
    #: Description of snapshot. Default is None.
    description = resource.Body("description")
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
    #: The ID of the volume this snapshot was taken of.
    volume_id = resource.Body("volume_id")

    def _action(self, session, body, microversion=None):
        """Preform backup actions given the message body."""
        url = utils.urljoin(self.base_path, self.id, 'action')
        resp = session.post(url, json=body,
                            microversion=self._max_microversion)
        exceptions.raise_from_response(resp)
        return resp

    def force_delete(self, session):
        """Force snapshot deletion.
        """
        body = {'os-force_delete': {}}
        self._action(session, body)

    def reset(self, session, status):
        """Reset the status of the snapshot.
        """
        body = {'os-reset_status': {'status': status}}
        self._action(session, body)

    def set_status(self, session, status, progress=None):
        """Update fields related to the status of a snapshot.
        """
        body = {'os-update_snapshot_status': {
            'status': status}}
        if progress is not None:
            body['os-update_snapshot_status']['progress'] = progress
        self._action(session, body)


SnapshotDetail = Snapshot
