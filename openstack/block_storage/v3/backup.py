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

from typing import cast, Any, Self
import warnings

import requests

from keystoneauth1 import adapter

from openstack.common import metadata
from openstack import exceptions
from openstack import resource
from openstack import utils
from openstack import warnings as os_warnings


class Backup(resource.Resource, metadata.MetadataMixin):
    """Volume Backup"""

    resource_key = "backup"
    resources_key = "backups"
    base_path = "/backups"

    # TODO(gtema): Starting from ~3.31(3.45) Cinder seems to support also fuzzy
    # search (name~, status~, volume_id~). But this is not documented
    # officially and seem to require microversion be set
    _query_mapping = resource.QueryParameters(
        "limit",
        "marker",
        "offset",
        "project_id",
        "name",
        "status",
        "volume_id",
        "sort_key",
        "sort_dir",
        "sort",
        all_projects="all_tenants",
    )

    # capabilities
    allow_fetch = True
    allow_create = True
    allow_delete = True
    allow_commit = True
    allow_list = True

    #: Properties
    #: backup availability zone
    availability_zone = resource.Body("availability_zone")
    #: The container backup in
    container = resource.Body("container")
    #: The date and time when the resource was created.
    created_at = resource.Body("created_at")
    #: data timestamp
    #: The time when the data on the volume was first saved.
    #: If it is a backup from volume, it will be the same as created_at
    #: for a backup. If it is a backup from a snapshot,
    #: it will be the same as created_at for the snapshot.
    data_timestamp = resource.Body('data_timestamp')
    #: backup description
    description = resource.Body("description")
    #: The UUID of the encryption key. Only included for encrypted volumes.
    encryption_key_id = resource.Body("encryption_key_id")
    #: Backup fail reason
    fail_reason = resource.Body("fail_reason")
    #: Force backup
    force = resource.Body("force", type=bool)
    #: has_dependent_backups
    #: If this value is true, there are other backups depending on this backup.
    has_dependent_backups = resource.Body('has_dependent_backups', type=bool)
    #: Indicates whether the backup mode is incremental.
    #: If this value is true, the backup mode is incremental.
    #: If this value is false, the backup mode is full.
    is_incremental = resource.Body("is_incremental", type=bool)
    #: A list of links associated with this volume. *Type: list*
    links = resource.Body("links", type=list)
    #: The backup metadata. New in version 3.43
    metadata = resource.Body('metadata', type=dict)
    #: backup name
    name = resource.Body("name")
    #: backup object count
    object_count = resource.Body("object_count", type=int)
    #: The UUID of the owning project.
    #: New in version 3.18
    project_id = resource.Body('os-backup-project-attr:project_id')
    #: The size of the volume, in gibibytes (GiB).
    size = resource.Body("size", type=int)
    #: The UUID of the source volume snapshot.
    snapshot_id = resource.Body("snapshot_id")
    #: backup status
    #: values: creating, available, deleting, error, restoring, error_restoring
    status = resource.Body("status")
    #: The date and time when the resource was updated.
    updated_at = resource.Body("updated_at")
    #: The UUID of the project owner. New in 3.56
    user_id = resource.Body('user_id')
    #: The UUID of the volume.
    volume_id = resource.Body("volume_id")
    #: The name of the volume.
    volume_name = resource.Body("volume_name")

    _max_microversion = "3.64"

    @classmethod
    def _transform_create_request(
        cls,
        session: adapter.Adapter,
        request: resource._Request,
        *,
        microversion: str | None,
    ) -> resource._Request:
        # The attribute is called "incremental" on create but "is_incremental"
        # on get; alias doesn't work here since our canonical name is the
        # get-side one.
        if isinstance(request.body, dict) and 'backup' in request.body:
            backup = request.body['backup']
            if 'is_incremental' in backup:
                backup['incremental'] = backup.pop('is_incremental')
        return request

    def _action(
        self,
        session: adapter.Adapter,
        body: dict[str, Any],
        microversion: str | None = None,
    ) -> requests.Response:
        """Preform backup actions given the message body."""
        url = utils.urljoin(self.base_path, self.id, 'action')
        resp = session.post(
            url, json=body, microversion=self._max_microversion
        )
        exceptions.raise_from_response(resp)
        return resp

    @classmethod
    def import_record(
        cls, session: adapter.Adapter, *, service: str, url: str
    ) -> Self:
        """Import information about a backup

        :param session: The session to use for making this request.
        :param service: The service used to perform the backup.
        :param url: An identifier string to locate the backup.
        :returns: The imported backup
        """
        session = cls._get_session(session)
        microversion = cls._get_microversion(session)
        url = utils.urljoin(cls.base_path, 'export_record')
        body = {
            'backup-record': {
                'backup_service': service,
                'backup_url': url,
            }
        }
        response = session.post(url, json=body, microversion=microversion)
        exceptions.raise_from_response(response)

        backup = cls()
        backup._translate_response(response)
        return backup

    def export_record(self, session: adapter.Adapter) -> dict[str, object]:
        """Export information about the backup

        :param session: The session to use for making this request.
        :return: The backup export record fields
        """
        url = utils.urljoin(self.base_path, self.id, "export_record")
        resp = session.get(url)
        exceptions.raise_from_response(resp)
        return cast(dict[str, object], resp.json())

    def export(self, session: adapter.Adapter) -> requests.Response:
        """Export information about the backup

        :param session: The session to use for making this request.
        :return: The backup export record fields
        """
        warnings.warn(
            "export is deprecated in favour of export_record and will be "
            "removed in a future release.",
            os_warnings.RemovedInSDK50Warning,
        )
        url = utils.urljoin(self.base_path, self.id, "export_record")
        resp = session.get(url)
        exceptions.raise_from_response(resp)
        return resp

    def restore(
        self,
        session: adapter.Adapter,
        volume_id: str | None = None,
        name: str | None = None,
    ) -> Self:
        """Restore current backup to volume

        :param session: The session to use for making this request.
        :param volume_id: The ID of the volume to restore the backup to.
        :param name: The name for new volume creation to restore.
        :return: Updated backup instance
        """
        url = utils.urljoin(self.base_path, self.id, "restore")
        body: dict[str, dict[str, Any]] = {'restore': {}}
        if volume_id:
            body['restore']['volume_id'] = volume_id
        if name:
            body['restore']['name'] = name
        if not (volume_id or name):
            raise exceptions.SDKException(
                'Either of `name` or `volume_id` must be specified.'
            )
        response = session.post(url, json=body)
        self._translate_response(response, resource_response_key='restore')
        return self

    def force_delete(self, session: adapter.Adapter) -> None:
        """Force backup deletion

        :param session: The session to use for making this request.
        :returns: None
        """
        body = {'os-force_delete': None}
        self._action(session, body)

    def reset_status(self, session: adapter.Adapter, status: str) -> None:
        """Reset the status of the backup

        :param session: The session to use for making this request.
        :returns: None
        """
        body = {'os-reset_status': {'status': status}}
        self._action(session, body)

    def reset(self, session: adapter.Adapter, status: str) -> None:
        warnings.warn(
            "reset is a deprecated alias for reset_status and will be "
            "removed in a future release.",
            os_warnings.RemovedInSDK60Warning,
        )
        self.reset_status(session, status)


BackupDetail = Backup
