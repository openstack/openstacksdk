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

    def create(self, session, prepend_key=True, base_path=None, **params):
        """Create a remote resource based on this instance.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`
        :param prepend_key: A boolean indicating whether the resource_key
                            should be prepended in a resource creation
                            request. Default to True.
        :param str base_path: Base part of the URI for creating resources, if
                              different from
                              :data:`~openstack.resource.Resource.base_path`.
        :param dict params: Additional params to pass.
        :return: This :class:`Resource` instance.
        :raises: :exc:`~openstack.exceptions.MethodNotSupported` if
                 :data:`Resource.allow_create` is not set to ``True``.
        """
        if not self.allow_create:
            raise exceptions.MethodNotSupported(self, "create")

        session = self._get_session(session)
        microversion = self._get_microversion(session)
        requires_id = (
            self.create_requires_id
            if self.create_requires_id is not None
            else self.create_method == 'PUT'
        )

        if self.create_exclude_id_from_body:
            self._body._dirty.discard("id")

        if self.create_method == 'POST':
            request = self._prepare_request(
                requires_id=requires_id,
                prepend_key=prepend_key,
                base_path=base_path,
            )
            # NOTE(gtema) this is a funny example of when attribute
            # is called "incremental" on create, "is_incremental" on get
            # and use of "alias" or "aka" is not working for such conflict,
            # since our preferred attr name is exactly "is_incremental"
            body = request.body
            if 'is_incremental' in body['backup']:
                body['backup']['incremental'] = body['backup'].pop(
                    'is_incremental'
                )
            response = session.post(
                request.url,
                json=request.body,
                headers=request.headers,
                microversion=microversion,
                params=params,
            )
        else:
            # Just for safety of the implementation (since PUT removed)
            raise exceptions.ResourceFailure(
                f"Invalid create method: {self.create_method}"
            )

        has_body = (
            self.has_body
            if self.create_returns_body is None
            else self.create_returns_body
        )
        self.microversion = microversion
        self._translate_response(response, has_body=has_body)
        # direct comparision to False since we need to rule out None
        if self.has_body and self.create_returns_body is False:
            # fetch the body if it's required but not returned by create
            return self.fetch(session)
        return self

    def _action(self, session, body, microversion=None):
        """Preform backup actions given the message body."""
        url = utils.urljoin(self.base_path, self.id, 'action')
        resp = session.post(
            url, json=body, microversion=self._max_microversion
        )
        exceptions.raise_from_response(resp)
        return resp

    def restore(self, session, volume_id=None, name=None):
        """Restore current backup to volume

        :param session: openstack session
        :param volume_id: The ID of the volume to restore the backup to.
        :param name: The name for new volume creation to restore.
        :return: Updated backup instance
        """
        url = utils.urljoin(self.base_path, self.id, "restore")
        body: dict[str, dict] = {'restore': {}}
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

    def force_delete(self, session):
        """Force backup deletion"""
        body = {'os-force_delete': None}
        self._action(session, body)

    def reset_status(self, session, status):
        """Reset the status of the backup"""
        body = {'os-reset_status': {'status': status}}
        self._action(session, body)

    def reset(self, session, status):
        warnings.warn(
            "reset is a deprecated alias for reset_status and will be "
            "removed in a future release.",
            os_warnings.RemovedInSDK60Warning,
        )
        self.reset_status(session, status)


BackupDetail = Backup
