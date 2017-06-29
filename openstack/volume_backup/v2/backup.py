#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
from openstack import resource2 as resource
from openstack import utils
from openstack.volume_backup import volume_backup_service


class CloudBackup(resource.Resource):
    """Cloud Backup"""
    resource_key = "backup"
    resources_key = "backups"
    base_path = "/cloudbackups"
    service = volume_backup_service.VolumeBackupService()

    # capabilities
    allow_create = True
    allow_delete = True

    #: Properties
    #: The volume to be backup
    volume_id = resource.Body("volume_id")
    #: The snapshot reference of volume to be backup
    snapshot_id = resource.Body("snapshot_id")
    #: Volume backup name
    name = resource.Body("name")
    #: Volume backup description
    description = resource.Body("description")
    #: The sync cloud backup job id
    job_id = resource.Body("id")

    def restore(self, session, volume_id):
        """Restore current backup to volume

        :param session: openstack session
        :param volume_id: the volume be restored
        :return:
        """
        url = utils.urljoin(self.base_path, self.id, "restore")
        endpoint_override = self.service.get_endpoint_override()
        body = {"restore": {"volume_id": volume_id}}
        response = session.post(url,
                                endpoint_filter=self.service,
                                endpoint_override=endpoint_override,
                                json=body,
                                headers={})
        self._translate_response(response)
        return self


class Backup(resource.Resource):
    """Backup"""
    resource_key = "backup"
    resources_key = "backups"
    base_path = "/backups"
    service = volume_backup_service.VolumeBackupService()

    _query_mapping = resource.QueryParameters(
        "name", "status", "volume_id"
    )

    # capabilities
    allow_create = True
    allow_delete = True
    allow_list = True
    allow_get = True

    #: Properties
    #: The volume to be backup
    volume_id = resource.Body("volume_id")
    #: The snapshot of volume which will be backup
    snapshot_id = resource.Body("snapshot_id")
    #: no meaning for now, first time full backup, then incremental by default
    incremental = resource.Body("incremental", type=bool)
    #: Force backup
    force = resource.Body("force", type=bool)
    #: backup name
    name = resource.Body("name")
    #: backup description
    description = resource.Body("description")
    #: backup status
    status = resource.Body("status")
    #: backup availability zone
    availability_zone = resource.Body("availability_zone")
    #: backup size
    size = resource.Body("size")
    #: backup object count
    object_count = resource.Body("object_count")
    #: The container backup in
    container = resource.Body("container")
    #: The container create at
    created_at = resource.Body("created_at")
    #: The tenant which backup belongs to
    tenant_id = resource.Body("os-bak-tenant-attr:tenant_id")
    #: Backup metadata
    service_metadata = resource.Body("service_metadata")
    #: Backup fail reason
    fail_reason = resource.Body("fail_reason")


class BackupDetail(Backup):
    base_path = '/backups/detail'

    # capabilities
    allow_create = False
    allow_get = False
    allow_update = False
    allow_delete = False
    allow_list = True
